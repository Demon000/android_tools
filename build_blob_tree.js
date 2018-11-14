#!/usr/bin/node

const path = require('path');
const exec = require('child_process').exec;

const isIgnoredLibrary = require('./ignored_libraries').isIgnoredLibrary;

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

	for (const char of unmatched) {
		if (library.includes(char)) {
			return false;
		}
	}

	if (isIgnoredLibrary(library)) {
		return false;
	}

	return true;
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

		const libraries = await getReferencedLibraries(filepath);
		const dependencies = libraries.filter(library => library != name);

		blobs[name] = {
			dependencies,
			arches: [arch],
		};
	}

	for (const dependencyName in blobs) {
		const dependencyBlob = blobs[dependencyName];
		let isIncluded = false;

		for (const dependantName in blobs) {
			if (dependencyName == dependantName) {
				continue;
			}

			dependantBlob = blobs[dependantName];

			if (!dependantBlob.dependencies.includes(dependencyName)) {
				continue;
			}

			isIncluded = true;

			dependencyBlob.dependencies.forEach(function(dependency) {
				if (!dependantBlob.dependencies.includes(dependency)) {
					dependantBlob.dependencies.push(dependency);
				}
			});
		}

		if (isIncluded) {
			delete blobs[dependencyName];
		}
	}

	console.log(JSON.stringify(blobs, null, 4));
}

const dirpath = path.resolve(process.argv[2]);
printBlobs(dirpath);
