const showConfirmationDialogFor = (selector) => {
  $(selector)[0].classList.toggle("toast--show");
  setTimeout(() => {
    $(selector)[0].classList.toggle("toast--show");
  }, 1500);
};

window["showConfirmationDialogFor"] = showConfirmationDialogFor;
