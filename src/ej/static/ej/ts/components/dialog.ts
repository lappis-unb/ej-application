const showConfirmationDialogFor = (selector) => {
  const dialogElement = $(selector)[0];
  dialogElement.classList.toggle("toast--show");
  setTimeout(() => {
    if(dialogElement){
      dialogElement.classList.toggle("toast--show");}
    }, 1500);
};

window["showConfirmationDialogFor"] = showConfirmationDialogFor;
