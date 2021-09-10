const fs = require("fs");

const PATH = "../source/";
const MODES = PATH + "modes";
const NEWPATH = "./result";

// THIS DEPENDS ON THE PREVIOUS PREPROCESSING STEP BEING DONE, SEE README.md or ../preprocess.py
function readAllModes() {
  global["_"] = require("lodash");

  global["window"] = {};
  global["settings"] = {};
  global["isLab"] = false; //TODO also need to handle the isLab cases

  require(`${PATH}config.js`);
  let commonSettings = require(`${MODES}/common.js`);

  _.map(commonSettings, function (v, k) {
    if (k in global) {
      console.error("warning, overwriting setting" + k);
    }
    global[k] = v;
  });

  const modes = {};

  fs.readdirSync(MODES).forEach((file) => {
    if (file.endsWith("_mode.js") && file != "npegl_mode.js") {
      global["settings"] = {};
      require(`${MODES}/${file}`);
      modes[file.split("_mode.js")[0]] = global["settings"];
    }
  });
  return modes;
}

function writeNewModes(modes) {
  for (let mode in modes) {
    const modeObj = modes[mode];
    modeObj.pop("attributes");
    modeObj.pop("structAttributes");
    let content = JSON.stringify(modeObj, null, 4);
    content = "export default " + content;
    fs.writeFile(`${NEWPATH}/${mode}_mode.js`, content, function (err) {
      if (err) {
        console.log("err writing", err);
      }
    });
  }
}

function writeSettingsToFile(modes) {
  for (let mode in modes) {
    let content = JSON.stringify(modes[mode], null, 4);
    fs.writeFile(`modes/${mode}.json`, content, function (err) {
      if (err) {
        console.log("err writing", err);
      }
    });
  }
}

const modes = readAllModes();
console.log(modes);
//for(let mode in modes) {
//modes[mode]['corpora'] = undefined;
//}

// does not change mode
//writeSettingsToFile(modes);
// changes mode
//writeNewModes(modes);
