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

module.exports = {
	execute,
};
