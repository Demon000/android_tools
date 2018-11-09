#!/usr/bin/node

const workerpool = require('workerpool');
const path = require('path');

const DEBUG = true;

const relativeFilesDirectory = process.argv[2];
const relativeFileStart = process.argv[3];

const filesDirectory = path.resolve(relativeFilesDirectory);
const fileStart = path.join(filesDirectory, relativeFileStart);

const pool = workerpool.pool(path.join(__dirname, 'library_worker.js'));
const foundPaths = [];

function addNeededLibraries(filePath, filesDirectory) {
	pool
	.exec('getNeededLibraries', [filePath, filesDirectory])
	.then(function(paths) {
		let newPaths = 0;

		paths.forEach(function(filePath) {
			if (foundPaths.includes(filePath)) {
				return;
			}

			console.log(path.relative(filesDirectory, filePath));
			foundPaths.push(filePath);
			newPaths++;

			addNeededLibraries(filePath, filesDirectory);
		});

		pool.terminate();
	})
	.catch(function (err) {
		console.error(err);
	});
}

addNeededLibraries(fileStart, filesDirectory);
