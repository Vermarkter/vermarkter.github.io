/**
 * migrate-images — Deno script / Edge Function
 *
 * Migrates all Unsplash image_url values in the `services` table
 * to Supabase Storage (bucket: 'service-images').
 *
 * Run locally:
 *   deno run --allow-net --allow-env supabase/functions/migrate-images/index.ts
 *
 * Deploy as Edge Function:
 *   supabase functions deploy migrate-images
 *
 * Required env vars:
 *   SUPABASE_URL          — e.g. https://xxxx.supabase.co
 *   SUPABASE_SERVICE_KEY  — service_role key (bypasses RLS; keep secret)
 *   DRY_RUN               — set to "true" to preview without writing (optional)
 */

import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const SUPABASE_URL        = Deno.env.get("SUPABASE_URL")        ?? ""
const SUPABASE_SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_KEY") ?? ""
const BUCKET              = "service-images"
const TABLE               = "services"
const DRY_RUN             = Deno.env.get("DRY_RUN") === "true"

// Content-Type → file extension map
const MIME_EXT: Record<string, string> = {
  "image/jpeg":  "jpg",
  "image/png":   "png",
  "image/webp":  "webp",
  "image/gif":   "gif",
  "image/avif":  "avif",
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function log(msg: string) {
  console.log(`[migrate-images] ${msg}`)
}

/** Derive file extension from a Content-Type header or fall back to "jpg". */
function extFromMime(contentType: string | null): string {
  if (!contentType) return "jpg"
  const base = contentType.split(";")[0].trim().toLowerCase()
  return MIME_EXT[base] ?? "jpg"
}

/** Sleep for `ms` milliseconds — used to avoid hammering Unsplash. */
const sleep = (ms: number) => new Promise(r => setTimeout(r, ms))

// ---------------------------------------------------------------------------
// Core migration logic
// ---------------------------------------------------------------------------

async function migrate() {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
    throw new Error(
      "Missing env vars: SUPABASE_URL and SUPABASE_SERVICE_KEY are required."
    )
  }

  const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY, {
    auth: { persistSession: false },
  })

  // 1. Fetch all services with Unsplash image_url
  log(`Fetching rows from '${TABLE}' where image_url contains 'unsplash.com'…`)

  const { data: services, error: fetchError } = await supabase
    .from(TABLE)
    .select("id, image_url")
    .like("image_url", "%unsplash.com%")

  if (fetchError) throw new Error(`DB fetch failed: ${fetchError.message}`)
  if (!services || services.length === 0) {
    log("No Unsplash images found. Nothing to do.")
    return
  }

  log(`Found ${services.length} record(s) to migrate. DRY_RUN=${DRY_RUN}`)
  console.log()

  const results = {
    success:  0,
    skipped:  0,
    failed:   0,
    errors:   [] as string[],
  }

  for (const service of services) {
    const { id, image_url } = service
    log(`→ [${id}] Fetching: ${image_url}`)

    try {
      // 2a. Download the image
      const response = await fetch(image_url, {
        headers: {
          // Polite User-Agent
          "User-Agent": "vermarkter-image-migrator/1.0 (+https://vermarkter.eu)",
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status} ${response.statusText}`)
      }

      const contentType = response.headers.get("content-type")
      const ext         = extFromMime(contentType)

      // 2b. Unique filename
      const filename    = `service-${id}.${ext}`
      const storagePath = filename

      // 2c. Read body as ArrayBuffer
      const buffer = await response.arrayBuffer()
      log(`   ✓ Downloaded ${buffer.byteLength} bytes — ${contentType} → ${filename}`)

      if (DRY_RUN) {
        log(`   [DRY RUN] Would upload to ${BUCKET}/${storagePath} and update DB.`)
        results.skipped++
        continue
      }

      // 2c. Upload to Supabase Storage
      const { error: uploadError } = await supabase.storage
        .from(BUCKET)
        .upload(storagePath, buffer, {
          contentType:  contentType ?? "image/jpeg",
          upsert:       true,   // overwrite if re-running the script
        })

      if (uploadError) {
        throw new Error(`Storage upload failed: ${uploadError.message}`)
      }

      // 2d. Get the public URL
      const { data: urlData } = supabase.storage
        .from(BUCKET)
        .getPublicUrl(storagePath)

      const publicUrl = urlData.publicUrl
      log(`   ✓ Uploaded → ${publicUrl}`)

      // 2e. Update the DB record
      const { error: updateError } = await supabase
        .from(TABLE)
        .update({ image_url: publicUrl })
        .eq("id", id)

      if (updateError) {
        throw new Error(`DB update failed: ${updateError.message}`)
      }

      log(`   ✓ DB updated for id=${id}`)
      results.success++
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err)
      log(`   ✗ FAILED for id=${id}: ${msg}`)
      results.errors.push(`id=${id}: ${msg}`)
      results.failed++
    }

    // Brief pause between requests — be polite to Unsplash
    await sleep(300)
    console.log()
  }

  // Summary
  console.log("=".repeat(60))
  log(`Done. Success: ${results.success} | Skipped (dry-run): ${results.skipped} | Failed: ${results.failed}`)
  if (results.errors.length > 0) {
    log("Errors:")
    results.errors.forEach(e => log(`  • ${e}`))
  }
}

// ---------------------------------------------------------------------------
// Entry point — works both as a standalone Deno script AND as an Edge Function
// ---------------------------------------------------------------------------

// Detect Edge Function environment (Deno Deploy exposes this global)
const isEdgeFunction = typeof (globalThis as Record<string, unknown>)["EdgeRuntime"] !== "undefined"

if (isEdgeFunction) {
  // Edge Function handler
  const { serve } = await import("https://deno.land/std@0.168.0/http/server.ts")
  serve(async (req: Request) => {
    // Simple auth guard — require Authorization: Bearer <SERVICE_KEY>
    const auth = req.headers.get("authorization") ?? ""
    if (!auth.startsWith("Bearer ") || auth.slice(7) !== SUPABASE_SERVICE_KEY) {
      return new Response(JSON.stringify({ error: "Unauthorized" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      })
    }

    try {
      await migrate()
      return new Response(JSON.stringify({ ok: true }), {
        headers: { "Content-Type": "application/json" },
      })
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err)
      return new Response(JSON.stringify({ error: msg }), {
        status: 500,
        headers: { "Content-Type": "application/json" },
      })
    }
  })
} else {
  // Local Deno script
  await migrate()
}
