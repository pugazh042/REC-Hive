(function () {
  window.RHConfirm = {
    ask(message) {
      return Promise.resolve(window.confirm(message));
    },
  };
})();
