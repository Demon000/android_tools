#!/usr/bin/node

const path = require('path');
const exec = require('child_process').exec;

function getBlobName(filepath) {
	return path.basename(filepath);
}

function getBlobArch(filepath) {
	if (filepath.includes('/lib/')) {
		return '32';
	} else if (filepath.includes('/lib64/')) {
		return '64';
	}

	return 'unknown';
}

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

function Blob(filepath) {
	this.name = getBlobName(filepath);
	this.arch = getBlobArch(filepath);
	this.getDependencies = async function() {
		this.dependencies = await getReferencedLibraries(filepath);
		return this.dependencies;
	};

	this.getJSON = function() {
		return {
			name: this.name,
			arch: this.arch,
			dependencies: this.dependencies,
		};
	};
}

async function findAllFiles(dirpath) {
	const FIND_COMMAND = `find ${dirpath} -type f`;

	const output = await execute(FIND_COMMAND);
	const files = output.trim().split('\n');

	return files;
}

const invalidExtensions = [
	'acdb',
	'alias',
	'apk',
	'b00',
	'b01',
	'b02',
	'b03',
	'b04',
	'bin',
	'cfg',
	'cil',
	'clearkey',
	'cng',
	'conf',
	'config',
	'dar',
	'dat',
	'db',
	'dep',
	'dict',
	'dlc',
	'elf',
	'ftcfg',
	'fw',
	'fw2',
	'gz',
	'ini',
	'json',
	'ko',
	'mdt',
	'pb',
	'pem',
	'png',
	'policy',
	'prog',
	'prop',
	'qcom',
	'qti',
	'qwsp',
	'rc',
	'sh',
	'sha256',
	'sql',
	'ttf',
	'txt',
	'uim',
	'wav',
	'widevine',
	'xml',
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
	const blobs = [];

	for (const filepath of filelist) {
		if (!isValidBlob(filepath)) {
			continue;
		}

		const blob = new Blob(filepath);
		const dependencies = await blob.getDependencies();
		console.log(JSON.stringify(blob.getJSON(), null, 4));
		blobs.push(blob);
	}
}

const dirpath = path.resolve(process.argv[2]);
printBlobs(dirpath);
