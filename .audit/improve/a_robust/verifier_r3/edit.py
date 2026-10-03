s=open('t_teacher_stores.py').read()
a=s.index("const a=document.getElementById('app');"); b=s.index("})()\")",a)
s=s[:a]+"const a=document.getElementById('app'); const body=a.querySelector('.tabs').nextElementSibling; return (body?body.innerText.replace(/\\\\s+/g,' ').trim():'NOBODY').slice(0,40)"+s[b:]
open('t_teacher_stores.py','w').write(s)
