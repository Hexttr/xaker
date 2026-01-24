const fs = require('fs');
const p = JSON.parse(fs.readFileSync('package.json'));
p.scripts.build = 'vite build';
fs.writeFileSync('package.json', JSON.stringify(p, null, 2));
console.log('OK');



