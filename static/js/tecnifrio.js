/* ============================================
   FUEL INJECTION — JS Global
   ============================================ */

// Toggle sidebar en móvil
document.addEventListener('DOMContentLoaded', function () {
  const sidebarToggle = document.getElementById('sidebarToggle');
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function (e) {
      e.preventDefault();
      document.getElementById('layoutSidenav_nav').classList.toggle('sb-sidenav-toggled');
    });
  }

  // Inicializar DataTables
  if (typeof $.fn.DataTable !== 'undefined') {
    $('.dataTable').DataTable({
      language: {
        url: '//cdn.datatables.net/plug-ins/1.13.8/i18n/es-ES.json',
      },
      pageLength: 15,
      order: [],
      responsive: true,
    });
  }

  // Auto-ocultar alertas bootstrap después de 5 segundos
  setTimeout(function () {
    document.querySelectorAll('.alert.alert-success, .alert.alert-info').forEach(function (el) {
      const bsAlert = new bootstrap.Alert(el);
      bsAlert.close();
    });
  }, 5000);

  // Confirmar eliminaciones con SweetAlert2
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      e.preventDefault();
      const msg = el.getAttribute('data-confirm') || '¿Estás seguro?';
      Swal.fire({
        title: msg,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sí, continuar',
        cancelButtonText: 'Cancelar',
      }).then((result) => {
        if (result.isConfirmed) {
          window.location.href = el.href || '#';
        }
      });
    });
  });

  // Mostrar nombre del archivo al seleccionarlo
  document.querySelectorAll('input[type="file"]').forEach(function (input) {
    input.addEventListener('change', function () {
      const label = this.nextElementSibling;
      if (label && label.classList.contains('custom-file-label')) {
        label.textContent = this.files[0] ? this.files[0].name : 'Seleccionar archivo…';
      }
    });
  });

  // Validación en tiempo real para formularios
  initFormValidation();
});

function initFormValidation() {
  const forms = document.querySelectorAll('form[novalidate]');
  
  forms.forEach(form => {
    const inputs = form.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
      // Validar al perder el foco
      input.addEventListener('blur', function() {
        validateField(this);
      });
      
      // Validar al escribir
      input.addEventListener('input', function() {
        if (this.classList.contains('is-invalid')) {
          validateField(this);
        }
      });
    });
    
    // Validar al enviar
    form.addEventListener('submit', function(e) {
      let isValid = true;
      inputs.forEach(input => {
        if (!validateField(input)) {
          isValid = false;
        }
      });
      
      if (!isValid) {
        e.preventDefault();
        // Mostrar mensaje de error general
        if (!form.querySelector('.form-general-error')) {
          const errorDiv = document.createElement('div');
          errorDiv.className = 'alert alert-danger form-general-error';
          errorDiv.innerHTML = '<i class="fas fa-exclamation-circle me-2"></i>Por favor, corrija los errores en el formulario.';
          form.insertBefore(errorDiv, form.firstChild);
        }
      }
    });
  });
}

function validateField(field) {
  const formGroup = field.closest('.col-12') || field.closest('.form-group');
  if (!formGroup) return true;
  
  // Remover clases previas
  field.classList.remove('is-valid', 'is-invalid');
  
  // Remover mensajes de error previos
  const existingError = formGroup.querySelector('.invalid-feedback');
  if (existingError) {
    existingError.remove();
  }
  
  // Validar campo requerido
  if (field.hasAttribute('required') && !field.value.trim()) {
    showFieldError(field, formGroup, 'Este campo es obligatorio.');
    return false;
  }
  
  // Validar patrón si existe
  if (field.hasAttribute('pattern') && field.value) {
    const pattern = new RegExp(field.getAttribute('pattern'));
    if (!pattern.test(field.value)) {
      const message = field.getAttribute('title') || 'El formato no es válido.';
      showFieldError(field, formGroup, message);
      return false;
    }
  }
  
  // Validar longitud mínima
  if (field.hasAttribute('minlength') && field.value.length < parseInt(field.getAttribute('minlength'))) {
    showFieldError(field, formGroup, `Debe tener al menos ${field.getAttribute('minlength')} caracteres.`);
    return false;
  }
  
  // Validar email
  if (field.type === 'email' && field.value) {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(field.value)) {
      showFieldError(field, formGroup, 'Ingrese un correo electrónico válido.');
      return false;
    }
  }
  
  // Validar teléfono (10 dígitos)
  if (field.name && field.name.includes('telefono') && field.value) {
    if (!/^\d{10}$/.test(field.value)) {
      showFieldError(field, formGroup, 'El teléfono debe tener 10 dígitos.');
      return false;
    }
  }
  
  // Validar número de documento (solo el campo de texto, NO el select tipo_documento)
  if (field.name === 'numero_documento' && field.value) {
    const form = field.closest('form');
    const tipoSelect = form ? form.querySelector('[name="tipo_documento"]') : null;
    const tipo = tipoSelect ? tipoSelect.value : '';

    if (tipo === 'PASAPORTE') {
      // Pasaporte: alfanumérico, sin espacios
      if (!/^[a-zA-Z0-9]+$/.test(field.value)) {
        showFieldError(field, formGroup, 'El pasaporte solo debe contener letras y números, sin espacios.');
        return false;
      }
    } else {
      // Cédula y RUC: solo dígitos
      if (!/^\d+$/.test(field.value)) {
        showFieldError(field, formGroup, 'El número de documento solo debe contener dígitos.');
        return false;
      }
      if (tipo === 'CEDULA' && field.value.length !== 10) {
        showFieldError(field, formGroup, 'La cédula debe tener exactamente 10 dígitos.');
        return false;
      }
      if (tipo === 'RUC' && field.value.length !== 13) {
        showFieldError(field, formGroup, 'El RUC debe tener exactamente 13 dígitos.');
        return false;
      }
    }
  }
  
  // Campo válido
  if (field.value.trim()) {
    field.classList.add('is-valid');
  }
  
  return true;
}

function showFieldError(field, formGroup, message) {
  field.classList.add('is-invalid');
  
  const errorDiv = document.createElement('div');
  errorDiv.className = 'invalid-feedback';
  errorDiv.textContent = message;
  formGroup.appendChild(errorDiv);
  
  // Animación de shake
  field.style.animation = 'shake 0.5s';
  setTimeout(() => {
    field.style.animation = '';
  }, 500);
}

// Agregar animación shake al CSS
const style = document.createElement('style');
style.textContent = `
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
  }
  
  .is-required::after {
    content: " *";
    color: #dc3545;
  }
  
  .form-control.is-valid, .form-select.is-valid {
    border-color: #198754;
    background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 8 8'%3e%3cpath fill='%23198754' d='M2.3 6.73L.6 4.53c-.4-1.04.46-1.4 1.1-.8l1.1 1.4 3.4-3.8c.6-.63 1.6-.27 1.2.7l-4 4.6c-.43.5-.8.4-1.1.1z'/%3e%3c/svg%3e");
    background-repeat: no-repeat;
    background-position: right calc(0.375em + 0.1875rem) center;
    background-size: calc(0.75em + 0.375rem) calc(0.75em + 0.375rem);
  }
  
  .form-control.is-invalid, .form-select.is-invalid {
    border-color: #dc3545;
    background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 12' width='12' height='12' fill='none' stroke='%23dc3545'%3e%3ccircle cx='6' cy='6' r='4.5'/%3e%3cpath stroke-linejoin='round' d='M5.8 3.6h.4L6 6.5z'/%3e%3ccircle cx='6' cy='8.2' r='.6' fill='%23dc3545' stroke='none'/%3e%3c/svg%3e");
    background-repeat: no-repeat;
    background-position: right calc(0.375em + 0.1875rem) center;
    background-size: calc(0.75em + 0.375rem) calc(0.75em + 0.375rem);
  }
  
  .invalid-feedback {
    display: block;
    font-size: 0.875em;
    margin-top: 0.25rem;
    color: #dc3545;
  }
`;
document.head.appendChild(style);
