var express = require('express');

  var app = express();

  var spawn = require('child_process').spawn;

  app.get('/garage-door/:action', function(req, res) {
    var action = req.params.action;
    const ls = spawn('/opt/pi_garage_trigger.py', [action]);

    ls.stdout.on('data', (data) => {
      console.log(`stdout: ${data}`);
      res.json({response: `output: ${data}`})
    });

    ls.stderr.on('data', (data) => {
      console.log(`stderr: ${data}`);
    });

    ls.on('close', (code) => {
      console.log(`invoked script exited with code ${code}`);
    });
  })

  app.listen(8888);
