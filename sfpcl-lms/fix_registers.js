const fs = require('fs');
const file = 'src/pages/registers/RegistersHub.tsx';
let code = fs.readFileSync(file, 'utf8');

if (!code.includes('useRole')) {
  code = code.replace(
    `import React, { useState } from 'react';`,
    `import React, { useState } from 'react';\nimport { useRole } from '../../contexts/RoleContext';`
  );
}

code = code.replace(
  `const RegistersHub: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);`,
  `const RegistersHub: React.FC = () => {
  const { can } = useRole();
  const [activeTab, setActiveTab] = useState(0);`
);

fs.writeFileSync(file, code);
console.log('fix complete');
