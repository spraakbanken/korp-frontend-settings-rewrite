const fs = require("fs");

const PATH = "../source/";
const MODES = PATH + "modes";
const NEWPATH = "./result";

// THIS DEPENDS ON THE PREVIOUS PREPROCESSING STEP BEING DONE, SEE README.md or ../preprocess.py
function readAllModes() {
  global["_"] = require("lodash");

  const modes = {};

  fs.readdirSync(MODES).forEach((file) => {
    if (file.endsWith("_mode.js")) {
      global["window"] = {};
      global["settings"] = {};
      // note that after running code, we can't know which corpora are
      // "lab corpora" or not, so this must be added manually
      global["isLab"] = true;

      require(`${PATH}config.js`);
      let commonSettings = require(`${MODES}/common.js`);

      _.map(commonSettings, function (v, k) {
        if (k in global) {
          console.error("warning, overwriting setting " + k);
        }
        global[k] = v;
      });
      require(`${MODES}/${file}`);
      modes[file.split("_mode.js")[0]] = global["settings"];

      // clean up global settings for peace of mind
      _.map(commonSettings, function (v, k) {
        delete global[k];
      });
    }
  });
  return modes;
}

function writeNewModesFiles(modes) {
  for (let mode in modes) {
    const modeObj = modes[mode];
    let content = JSON.stringify(modeObj, null, 4);
    fs.writeFile(`${NEWPATH}/${mode}.json`, content, function (err) {
      if (err) {
        console.log("err writing", err);
      }
    });
  }
}

const modes = readAllModes();
writeNewModesFiles(modes);
