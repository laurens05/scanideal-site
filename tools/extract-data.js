const fs=require('fs');
const L=fs.readFileSync(process.argv[2],'utf8').split('\n');
const a=L.findIndex(l=>l.startsWith("    const B = 'https://scanideal1"));
const b=L.findIndex(l=>l.startsWith("    const refs = ["));
const code=L.slice(a,b).join('\n');

const f=new Function(code+'\n;return {brands,products,I};');
const r=f();
fs.writeFileSync(process.argv[3],JSON.stringify({brands:r.brands,products:r.products},null,1));
console.log(r.brands.length,r.products.length,Object.keys(r.brands[0]));
