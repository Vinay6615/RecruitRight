document.addEventListener('DOMContentLoaded', ()=>{
  const form = document.querySelector('form');
  if (!form) return;
  form.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    try {
      const res = await fetch('/api/auth/signin', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username,password})});
      const j = await res.json();
      alert(j.message);
      if (j.ok) window.location.href = '/upload';
    } catch(e){ alert('Sign in failed'); }
  });
});