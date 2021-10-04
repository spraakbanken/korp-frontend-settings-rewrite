const fs = require("fs");

const PATH = "../source/";
const MODES = PATH + "modes";
const NEWPATH = "./result";

// THIS DEPENDS ON THE PREVIOUS PREPROCESSING STEP BEING DONE, SEE README.md or ../preprocess.py
function readMode(modeFile) {
  global["_"] = require("lodash");

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
  require(`../${modeFile}`);
  return global["settings"];
}

function writeMode(modeFile, modeObj) {
  const filename = modeFile.split("/")[2];
  const mode = filename.slice(0, filename.lastIndexOf("_"));
  let content = JSON.stringify(modeObj, null, 4);
  fs.writeFile(`${NEWPATH}/${mode}.json`, content, function (err) {
    if (err) {
      console.log("err writing", err);
    }
  });
}

const modeFile = process.argv[2];
const mode = readMode(modeFile);
writeMode(modeFile, mode);
