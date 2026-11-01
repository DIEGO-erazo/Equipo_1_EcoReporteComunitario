// Botón del ojo junto a los campos de contraseña: muestra u oculta lo que se escribe.
document.addEventListener('click', (evento) => {
  const boton = evento.target.closest('[data-ver-contrasena]');
  if (!boton) return;
  const campo = boton.parentElement.querySelector('input');
  const mostrar = campo.type === 'password';
  const texto = mostrar ? 'Ocultar contraseña' : 'Mostrar contraseña';
  campo.type = mostrar ? 'text' : 'password';
  boton.setAttribute('aria-pressed', String(mostrar));
  boton.setAttribute('aria-label', texto);
  boton.title = texto;
  boton.querySelector('.ojo-abierto').classList.toggle('d-none', mostrar);
  boton.querySelector('.ojo-cerrado').classList.toggle('d-none', !mostrar);
});
