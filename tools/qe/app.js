/* Minimal QE input generator with CIF preview */

// --- Helpers ---
const $ = (id) => document.getElementById(id);
const val = (id) => $(id).value.trim();

function parseAtoms(text) {
  // lines: "Si 0.0 0.0 0.0" (fractional)
  return text
    .split(/\r?\n/)
    .map(l => l.trim())
    .filter(Boolean)
    .map(l => {
      const [sym, x, y, z] = l.split(/\s+/);
      return { sym, x: parseFloat(x), y: parseFloat(y), z: parseFloat(z) };
    });
}

function guessATOMIC_SPECIES(atoms) {
  // unique symbols with placeholder masses & pseudo names
  const uniq = [...new Set(atoms.map(a => a.sym))];
  return uniq.map(sym => ({
    sym,
    mass: 28.085, // simple placeholder; users will edit if needed
    pseudo: `${sym}.upf`
  }));
}

function kpointsText(kx, ky, kz) {
  // Monkhorst-Pack
  return `K_POINTS automatic
 ${kx} ${ky} ${kz} 0 0 0`;
}

function systemBlock({ecutwfc, ecutrho, occupations, smearing, degauss, nspin, startMag}) {
  const lines = [
    "SYSTEM",
    `  ecutwfc = ${ecutwfc}`,
    `  ecutrho = ${ecutrho}`,
    `  occupations = '${occupations}'`
  ];
  if (occupations === 'smearing') {
    lines.push(`  smearing = '${smearing}'`);
    lines.push(`  degauss = ${degauss}`);
  }
  if (nspin === "2") {
    lines.push("  nspin = 2");
    lines.push(`  starting_magnetization(1) = ${startMag}`);
  }
  return "&" + lines.join(",\n") + "\n/";
}

function controlBlock(calcType) {
  const defaults = [
    "CONTROL",
    `  calculation = '${calcType}'`,
    "  prefix = 'qe'",
    "  outdir = './tmp'",
    "  pseudo_dir = './pseudos'"
  ];
  return "&" + defaults.join(",\n") + "\n/";
}

function electronsBlock() {
  return `&ELECTRONS
  conv_thr = 1.0d-8,
  mixing_beta = 0.7
/`;
}

function ionsBlockIfNeeded(calcType) {
  if (calcType === 'relax' || calcType === 'vc-relax') {
    return `&IONS
  ion_dynamics = 'bfgs'
/`;
  }
  return "";
}

function cellBlockIfNeeded(calcType) {
  if (calcType === 'vc-relax') {
    return `&CELL
  cell_dynamics = 'bfgs'
/`;
  }
  return "";
}

function atomicSpeciesBlock(species) {
  // sym mass pseudo
  const lines = species.map(s => `${s.sym} ${s.mass.toFixed(3)} ${s.pseudo}`);
  return `ATOMIC_SPECIES
${lines.join('\n')}`;
}

function fromManualCell({a,b,c,alpha,beta,gamma}) {
  // For simplicity use celldm via lattice parameters (Å) → use A/B/C Angstrom + angles: use CELL_PARAMETERS (angstrom)
  const A = parseFloat(a), B = parseFloat(b), C = parseFloat(c);
  const al = parseFloat(alpha), be = parseFloat(beta), ga = parseFloat(gamma);
  return {
    CELL_PARAMETERS: `CELL_PARAMETERS angstrom
${A} 0.0 0.0
0.0 ${B} 0.0
0.0 0.0 ${C}`,
    // In general, for non-orthorhombic you’d convert angles → vectors.
    // To keep robust and simple, this block assumes orthorhombic if angles == 90.
    // If angles differ, we still print diagonal vectors (note: user should edit).
    WARNING: (al !== 90 || be !== 90 || ga !== 90)
      ? "!! Non-90° angles entered; vectors are set as diagonal. Edit CELL_PARAMETERS as needed."
      : ""
  };
}

function atomicPositionsBlock(atoms) {
  const lines = atoms.map(a => `${a.sym} ${a.x} ${a.y} ${a.z}`);
  return `ATOMIC_POSITIONS crystal
${lines.join('\n')}`;
}

function generateQE() {
  const calcType = val('calcType');
  const ecutwfc = val('ecutwfc') || "50";
  const ecutrho = val('ecutrho') || "400";
  const occupations = val('occupations');
  const smearing = val('smearing');
  const degauss = val('degauss') || "0.02";
  const nspin = val('nspin');
  const startMag = val('startMag') || "0.0";
  const kx = val('kx') || "6";
  const ky = val('ky') || "6";
  const kz = val('kz') || "6";

  let atoms = parseAtoms(val('atoms'));
  if (atoms.length === 0) {
    // placeholder if only CIF is used (positions not parsed to POS yet)
    atoms = [{sym:'Si',x:0,y:0,z:0},{sym:'Si',x:0.25,y:0.25,z:0.25}];
  }
  const species = guessATOMIC_SPECIES(atoms);
  const cell = fromManualCell({
    a: val('a'), b: val('b'), c: val('c'),
    alpha: val('alpha'), beta: val('beta'), gamma: val('gamma')
  });

  const text = `&${controlBlock(calcType).slice(1)}

${systemBlock({ecutwfc, ecutrho, occupations, smearing, degauss, nspin, startMag)}

${electronsBlock()}

${ionsBlockIfNeeded(calcType)}

${cellBlockIfNeeded(calcType)}

${atomicSpeciesBlock(species)}

${atomicPositionsBlock(atoms)}

${kpointsText(kx,ky,kz)}
${cell.WARNING ? `

! ${cell.WARNING}` : ""}`.replace(/\n{3,}/g, '\n\n');

  $('qeOutput').value = text.trim();
  return { text, calcType };
}

function download(filename, text) {
  const blob = new Blob([text], {type: "text/plain;charset=utf-8"});
  saveAs(blob, filename);
}

function slurmScript(calcType) {
  return `#!/bin/bash
#SBATCH --job-name=qe_${calcType}
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --time=24:00:00
#SBATCH --partition=standard
#SBATCH --output=qe_%j.out

module load quantum-espresso
export OMP_NUM_THREADS=1

pw.x -in input.in > output.log
`;
}

function readme(calcType) {
  return `# Quantum ESPRESSO: ${calcType}

## Files
- \`input.in\` — Generated pw.x input.
- \`job.sh\`  — Example SLURM script.

## Run (local)
\`\`\`bash
pw.x -in input.in > output.log
\`\`\`

## Run (SLURM)
\`\`\`bash
sbatch job.sh
\`\`\`

> Note: Edit pseudopotential filenames and \`pseudo_dir\` to match your environment.
`;
}

// --- Events ---
$('generateBtn').addEventListener('click', () => {
  const { text, calcType } = generateQE();
  // ready for download buttons
});

$('downloadQE').addEventListener('click', () => {
  const { text } = generateQE();
  download('input.in', text);
});
$('downloadSLURM').addEventListener('click', () => {
  const { calcType } = generateQE();
  download('job.sh', slurmScript(calcType));
});
$('downloadREADME').addEventListener('click', () => {
  const { calcType } = generateQE();
  download('README.md', readme(calcType));
});

// --- CIF preview ---
let glviewer = null;
function ensureViewer() {
  if (!glviewer) {
    glviewer = $3Dmol.createViewer("viewer", { backgroundColor: "white" });
  }
  return glviewer;
}

$('loadCIF').addEventListener('click', () => {
  const cif = $('cifText').value.trim();
  if (!cif) {
    alert('Paste CIF text first.');
    return;
  }
  const viewer = ensureViewer();
  viewer.clear();
  viewer.addModel(cif, "cif");
  viewer.setStyle({}, {stick:{}, sphere:{scale:0.2}});
  viewer.zoomTo();
  viewer.render();
});
