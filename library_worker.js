const workerpool = require('workerpool');
const exec = require('child_process').exec;

const ignoredLibraries = require('./ignored_libraries');

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

function isImportantLibrary(library) {
	return !ignoredLibraries.includes(library);
}

async function getLibraryStrings(path) {
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

async function getFileArch(path, archFn) {
	const FILE_COMMAND = `file ${path}`;
	const ARCH_REGEX = /ELF \d{2}-bit/;

	const output = await execute(FILE_COMMAND);
	const arch = output.match(ARCH_REGEX)[0];

	return arch;
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
		console.log(`missing: ${library}`)
	} else {
		paths = output.trim().split('\n')
	}

	return paths;
}

async function getPathsForLibraries(libraries, filesDirectory) {
	let allPaths = [];

	for (const library of libraries) {
		const paths = await getPathsForLibrary(library, filesDirectory);
		allPaths = allPaths.concat(paths);
	}

	return allPaths;
}

async function filterFilesWithArch(paths, targetArch) {
	const matchingPaths = [];

	for (const path of paths) {
		const fileArch = await getFileArch(path);
		if (fileArch == targetArch) {
			matchingPaths.push(path);
		}
	}

	return matchingPaths;
}

async function getNeededLibraries(path, filesDirectory) {
	const fileArch = await getFileArch(path);

	const libraries = await getLibraryStrings(path);

	const allPaths = await getPathsForLibraries(libraries, filesDirectory);
	const paths = await filterFilesWithArch(allPaths, fileArch);

	return paths;
}

workerpool.worker({
	getNeededLibraries
});
