# Product Auto Reference

## Descripción
**Product Auto Reference** es un módulo para Odoo 18 diseñado para automatizar la generación de Referencias Internas (`default_code`) en los productos. Utiliza secuencias configurables (`ir.sequence`) de Odoo para asegurar que cada producto introducido en el sistema tenga un identificador único, estructurado y estandarizado sin necesidad de ingresarlo manualmente.

## Objetivos
- **Automatizar la codificación:** Generar y asignar automáticamente la Referencia Interna al momento de crear un nuevo producto.
- **Flexibilidad por Categoría:** Permitir configurar secuencias distintas y personalizadas para cada Categoría de Producto (ej. Productos Terminados pueden tener un prefijo diferente a las Materias Primas).
- **Secuencia Global de Respaldo:** Proveer una secuencia por defecto general para asegurar que ningún producto se quede sin referencia, incluso si su categoría específica no está configurada.
- **Respetar la entrada manual:** Dar prioridad total a la acción del usuario. Si el usuario introduce explícitamente un código al crear el producto, el sistema respeta ese código y no lo sobrescribe.
- **Soporte Multi-compañía:** Manejar de forma correcta y segura la numeración en entornos multi-compañía, priorizando las secuencias de la compañía activa y permitiendo secuencias globales compartidas.
- **Garantizar la Unicidad (Prevención de colisiones):** Asegurar matemáticamente que el código generado no es utilizado por algún otro producto existente previniendo errores de duplicidad silenciosos.

## ¿Cómo Funciona?

El módulo interviene de manera transparente al momento de ejecutar la acción de creación de un producto (`product.template`), y aplica un conjunto estricto de reglas de validación en el siguiente orden:

1. **Regla de Entrada Manual:**
   - El sistema revisa si el campo referencial (`default_code`) viene con algún valor escrito explícitamente por el usuario o desde una plantilla.
   - Si tiene algún valor, **el módulo no interfiere** y asume que es una codificación personalizada que debe respetarse.

2. **Secuencia por Categoría de Producto:**
   - Si el campo del código está en blanco, el módulo inspecciona la "Categoría de Producto" (`product.category`) que se le acaba de asignar al nuevo producto.
   - Si dicha categoría tiene una secuencia asignada en su nuevo campo de configuración **Reference Sequence**, el módulo tomará esa secuencia y generará un correlativo (respetando además, que la secuencia pertenezca a la misma compañía o que sea una secuencia compartida).

3. **Secuencia Global por Defecto:**
   - Si la categoría está vacía, o no cuenta con ninguna secuencia asignada, el módulo activará el "modo de contingencia" o "fallback".
   - Buscará una secuencia global en el sistema cuyo código técnico es `product.auto.ref.default`. Por defecto, el módulo instala automáticamente esta secuencia durante la instalación, por lo cual se asegura que de todas formas se generará un código consecutivo para el producto, también evaluando el contexto respectivo de la compañía.

### Prevención de Colisiones Segura
Para asegurar que no hayan errores de base de datos cuando dos usuarios crean productos a la vez, o que por algún motivo la secuencia de turno haya quedado por detrás de un código ya existente:
El módulo solicita el siguiente número a la secuencia seleccionada. Antes de asignarlo definitivamente, realiza una validación exhaustiva en la tabla de productos (incluyendo productos archivados) verificando si ese código está libre. 
- Si no está ocupado, se lo asigna finalmente al nuevo producto.
- Si el código ya está siendo utilizado, pedirá un nuevo correlativo iterando este paso en bucle. Todo esto sucede en fracciones de segundo y hasta un límite restrictivo de 1,000 intentos, para prevenir que el servidor caiga en un bucle infinito en caso de configuraciones incorrectas extremas.

## Configuración y Usabilidad

1. **Instalación de Base:**
   Tras la instalación regular del módulo en Odoo, el sistema preparará su funcionamiento base y auto-creará un registro para la secuencia global que está lista para funcionar de inmediato.

2. **Asignación de Secuencias a Nivel Categoría:**
   - Dirígete al menú: **Inventario > Configuración > Productos > Categorías de Productos**.
   - Haz clic y edita la categoría que deseas personalizar.
   - Encontrarás un nuevo campo llamado **Reference Sequence**. Ahí podrás seleccionar y enlazar una secuencia a la categoría (en el sistema, las secuencias permitidas son aquellas con código numérico asociado que inicie con `product.auto.ref`). Solo los productos con esta Categoría específica recibirán códigos con esta secuencia.

3. **Control y Edición de Secuencias Centralizado:**
   - Para evitar estar escarbando en la vista técnica de Odoo, el módulo agrega automáticamente el menú **Inventario > Configuración > Product Sequences**.
   - Desde este lugar, podrás gestionar cómodamente todos los prefijos (ej `PT-`, `MP-`, etc), longitud sugerida del correlativo, y compañía de las secuencias a utilizar.

## Requisitos y Dependencias
* Depende nativamente del módulo base de productos (`product`) e inventario (`stock`) para su inyección.

---
**Autor:** Rachel Duarte - Alesco Perú  
**Versión Compatibilidad:** Odoo 18.0  
**Licencia:** LGPL-3  
