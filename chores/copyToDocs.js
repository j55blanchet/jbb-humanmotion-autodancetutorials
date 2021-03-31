/* eslint-disable @typescript-eslint/no-var-requires */
/* eslint-disable import/no-extraneous-dependencies */

const fs = require('fs');
const fse = require('fs-extra');

fs.copyFileSync('docs/CNAME', 'dist/CNAME');

fs.rmdirSync('docs', {
  recursive: true,
});

fse.copySync('dist', 'docs');
