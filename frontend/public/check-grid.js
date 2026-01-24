// Скрипт для проверки сетчатого фона в консоли браузера
// Выполните в консоли: 
// fetch('/app/check-grid.js').then(r => r.text()).then(eval)

(function() {
  console.log('=== Проверка сетчатого фона ===');
  
  // Проверка элемента с data-testid
  const gridElement = document.querySelector('[data-testid="grid-background"]');
  console.log('1. Элемент с data-testid="grid-background":', gridElement);
  
  if (gridElement) {
    console.log('2. Стили элемента:', window.getComputedStyle(gridElement));
    console.log('3. backgroundImage:', window.getComputedStyle(gridElement).backgroundImage);
    console.log('4. position:', window.getComputedStyle(gridElement).position);
    console.log('5. zIndex:', window.getComputedStyle(gridElement).zIndex);
    console.log('6. opacity:', window.getComputedStyle(gridElement).opacity);
    console.log('7. width:', window.getComputedStyle(gridElement).width);
    console.log('8. height:', window.getComputedStyle(gridElement).height);
    console.log('9. top:', window.getComputedStyle(gridElement).top);
    console.log('10. left:', window.getComputedStyle(gridElement).left);
  } else {
    console.error('❌ Элемент с data-testid="grid-background" НЕ НАЙДЕН!');
  }
  
  // Проверка Layout
  const layout = document.querySelector('.min-h-screen.bg-black.flex.relative');
  console.log('11. Layout элемент:', layout);
  if (layout) {
    console.log('12. Дочерние элементы Layout:', layout.children);
    console.log('13. Количество дочерних элементов:', layout.children.length);
  }
  
  // Проверка Logo
  const logo = document.querySelector('[data-testid="logo-svg"]');
  console.log('14. Logo элемент:', logo);
  
  console.log('=== Конец проверки ===');
})();

