import paper from "paper";
import { ForceLayout } from "./clusterviz/force";
import { initSvg } from "./clusterviz/shape";

//
// INITIALIZATION
//
export function initializeForceLayout(elem = "#canvas", data = null) {
  // Setup canvas
  let canvas: HTMLCanvasElement = document.querySelector(elem);
  paper.setup(canvas);
  // Svg symbol
  initSvg(new paper.Raster());

  // Init simulation
  let layout = ForceLayout.fromJSON(data);
  paper.view.onFrame = (ev) => layout.update(Math.min(ev.delta, 0.032));
}
window["initializeForceLayout"] = initializeForceLayout;
