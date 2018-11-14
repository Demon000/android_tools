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

const ignoredLibraries = [
	'libbase.so',
	'libc++.so',
	'libc.so',
	'libcutils.so',
	'libdl.so',
	'libhardware.so',
	'libhardware_legacy.so',
	'libhidlbase.so',
	'libhidltransport.so',
	'libhwbinder.so',
	'liblog.so',
	'libm.so',
	'libutils.so',
	'libz.so',
];

function isValidLibrary(library) {
	const unmatched = [' ', '/', '<', '>'];

	if (!library.endsWith('.so')) {
		return false;
	}

	if (ignoredLibraries.includes(library)) {
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

async function getBlobArch(filepath) {
	for (const extension of invalidExtensions) {
		if (filepath.endsWith(extension)) {
			return 'unknown';
		}
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

async function printBlobs(dirpath) {
	const filelist = await findAllFiles(dirpath);
	const blobs = {};
	const usage = {};

	for (const filepath of filelist) {
		const name = getBlobName(filepath);
		if (blobs[name]) {
			blobs[name].arches = ['32', '64'];
			continue;
		}

		const arch = await getBlobArch(filepath);
		if (arch == 'unknown') {
			continue;
		}

		if (!usage[name]) {
			usage[name] = 0;
		}

		const libraries = await getReferencedLibraries(filepath)
		const dependencies = libraries.filter(library => library != name);

		dependencies.forEach(function(library) {
			if (usage[library]) {
				usage[library]++;
			} else {
				usage[library] = 1;
			}
		});

		blobs[name] = {
			dependencies,
			arches: [arch],
		};
	}

	const usageList = [];
	for (const library in usage) {
		usageList.push([library, usage[library]]);
	}

	usageList.sort(function(a, b) {
		return a[1] - b[1];
	});

	console.log(JSON.stringify(usageList, null, 4));
}

const dirpath = path.resolve(process.argv[2]);
printBlobs(dirpath);
