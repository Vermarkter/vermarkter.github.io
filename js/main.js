function calculate() {
  const budget = parseFloat(document.getElementById('budget').value);
  const multiplier = parseFloat(document.getElementById('platform').value);
  
  const clicks = Math.round((budget / 0.5) * multiplier);
  const leads = Math.round(clicks * 0.04); 

  document.getElementById('res-clicks').innerText = clicks.toLocaleString();
  document.getElementById('res-leads').innerText = leads.toLocaleString();
}

const bInput = document.getElementById('budget');
const bRange = document.getElementById('budget-range');
if(bInput && bRange) {
    bInput.addEventListener('input', (e) => { bRange.value = e.target.value; calculate(); });
    bRange.addEventListener('input', (e) => { bInput.value = e.target.value; calculate(); });
}
