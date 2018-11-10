const DEBUG = false;

const exec = require('child_process').exec;

const isImportantLibrary = require('./ignored_libraries').isImportantLibrary;

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

async function getReferencedLibraries(path) {
	const STRINGS_COMMAND = `strings "${path}" | grep -F ".so"`;

	const output = await execute(STRINGS_COMMAND);
	let libraries;

	if (output == '') {
		libraries = [];
	} else {
		libraries = output.trim().split('\n')
	}

	return libraries.filter(isImportantLibrary);
}

function toLinuxWildcardLibrary(library) {
	return library.replace('%s', '*');
}

async function getPathsForLibrary(library, filesDirectory) {
	const wildcard = toLinuxWildcardLibrary(library);
	const FIND_COMMAND = `find ${filesDirectory} -name "${wildcard}"`;

	const output = await execute(FIND_COMMAND);
	let paths = output.trim().split('\n');

	if (output == '') {
		paths = [];
		if (DEBUG) {
			console.log(`missing: ${library}`);
		}
	} else {
		paths = output.trim().split('\n')
	}

	return paths;
}

async function getFileArch(path, archFn) {
	const FILE_COMMAND = `file ${path}`;
	const ARCH_REGEX = /ELF \d{2}-bit/;

	const output = await execute(FILE_COMMAND);
	const arch = output.match(ARCH_REGEX)[0];

	return arch;
}

module.exports = {
	execute,
	getReferencedLibraries,
	toLinuxWildcardLibrary,
	getPathsForLibrary,
	getFileArch,
};
