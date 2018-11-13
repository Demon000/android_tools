#!/usr/bin/node

const path = require('path');
const exec = require('child_process').exec;

function execute(command, outputFn) {
	return new Promise(function(resolve, reject) {
		exec(command, {
			maxBuffer: 1024 * 1024 * 512,
		}, function(error, stdout, stderr) {
			if (error) {
				console.error(error);
				stdout = '';
			}

			if (stderr) {
				console.log(stderr);
			}
			
			resolve(stdout);
		});
	});
}

function isValidLibrary(library) {
	const unmatched = [' ', '/', '<', '>'];

	if (!library.endsWith('.so')) {
		return false;
	}

	return unmatched.every(function(char) {
		return !library.includes(char);
	});
}

async function getReferencedLibraries(path) {
	const STRINGS_COMMAND = `strings "${path}"`;

	const output = await execute(STRINGS_COMMAND);
	let libraries;

	if (output == '') {
		libraries = [];
	} else {
		libraries = output.trim().split('\n')
	}

	return libraries.filter(isValidLibrary);
}

function getBlobName(filepath) {
	return path.basename(filepath);
}

async function getBlobArch(filepath) {
	if (filepath.includes('/lib/')) {
		return '32';
	} else if (filepath.includes('/lib64/')) {
		return '64';
	}

	const FILE_COMMAND = `file ${filepath}`;
	const ARCH_REGEX = /(ELF )(\d{2})(-bit)/;
	const output = await execute(FILE_COMMAND);
	const matches = output.match(ARCH_REGEX);
	if (matches) {
		return matches[2];
	} else {
		return 'unknown';
	}
}

async function findAllFiles(dirpath) {
	const FIND_COMMAND = `find ${dirpath} -type f`;

	const output = await execute(FIND_COMMAND);
	const files = output.trim().split('\n');

	return files;
}

const invalidExtensions = [
	'.acdb',
	'.alias',
	'.apk',
	'.b00',
	'.b01',
	'.b02',
	'.b03',
	'.b04',
	'.bin',
	'.cfg',
	'.cil',
	'.cng',
	'.conf',
	'.config',
	'.dar',
	'.dat',
	'.db',
	'.dep',
	'.dict',
	'.dlc',
	'.elf',
	'.ftcfg',
	'.fw',
	'.fw2',
	'.gz',
	'.ini',
	'.json',
	'.ko',
	'.mdt',
	'.pb',
	'.pem',
	'.png',
	'.policy',
	'.prog',
	'.prop',
	'.qcom',
	'.qti',
	'.qwsp',
	'.rc',
	'.sh',
	'.sha256',
	'.sql',
	'.ttf',
	'.txt',
	'.uim',
	'.wav',
	'.xml',
];

function isValidBlob(filepath) {
	for (const extension of invalidExtensions) {
		if (filepath.endsWith(extension)) {
			return false;
		}
	}

	return true;
}

async function printBlobs(dirpath) {
	const filelist = await findAllFiles(dirpath);
	const blobs = {};

	for (const filepath of filelist) {
		if (!isValidBlob(filepath)) {
			continue;
		}

		const arch = await getBlobArch(filepath);
		if (arch == 'unknown') {
			continue;
		}

		const name = getBlobName(filepath);
		if (blobs[name]) {
			blobs[name].arches.push(arch);
			continue;
		}

		const libraries = await getReferencedLibraries(filepath)
		const dependencies = libraries.filter(library => library != name);

		blobs[name] = {
			dependencies,
			arches: [arch],
		};
	}

	console.log(JSON.stringify(blobs, null, 4));
}

const dirpath = path.resolve(process.argv[2]);
printBlobs(dirpath);
