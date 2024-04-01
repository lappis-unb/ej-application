const showConfirmationDialogFor = (selector) => {
  try {
    const dialogElement = $(selector)[0];
    dialogElement.classList.toggle("toast--show");
    setTimeout(() => {
      if (dialogElement) {
        dialogElement.classList.toggle("toast--show");
      }
    }, 1500);
  } catch (error) {
    console.info(`could not find ${selector} DOM element.`);
  }
};

window["showConfirmationDialogFor"] = showConfirmationDialogFor;
