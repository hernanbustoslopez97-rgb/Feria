import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuración inicial de la página
st.set_page_config(page_title="Gestión Integral - Mercado Mayorista", page_icon="📦", layout="wide")

# Archivos de persistencia local
FILE_INVENTARIO = "inventario.csv"
FILE_VENTAS = "ventas.csv"
FILE_CLIENTES = "clientes_ctas_ctes.csv"
FILE_PROVEEDORES = "proveedores_ctas_ctes.csv"

def inicializar_archivos():
    if not os.path.exists(FILE_INVENTARIO) or os.path.getsize(FILE_INVENTARIO) == 0:
        df_inv = pd.DataFrame(columns=["ID", "Fecha_Ingreso", "Producto", "Proveedor", "Bultos_Ingresados", "Costo_Unitario", "Costo_Logistica_Prorrateo", "Costo_Final_Unitario", "Stock_Actual", "Tipo_Logistica", "Estado"])
        df_inv.to_csv(FILE_INVENTARIO, index=False)
    
    if not os.path.exists(FILE_VENTAS) or os.path.getsize(FILE_VENTAS) == 0:
        df_v = pd.DataFrame(columns=["ID_Venta", "Fecha", "Cliente", "Tipo_Cliente", "Detalle_Items", "Total_Bultos", "Monto_Total", "Costo_CMV", "Medio_Pago", "Estado_Pago"])
        df_v.to_csv(FILE_VENTAS, index=False)

    if not os.path.exists(FILE_CLIENTES) or os.path.getsize(FILE_CLIENTES) == 0:
        df_c = pd.DataFrame(columns=["Fecha", "Cliente", "Operacion", "Debe", "Haber", "Saldo_Pendiente", "Medio_Pago"])
        df_c.to_csv(FILE_CLIENTES, index=False)

    if not os.path.exists(FILE_PROVEEDORES) or os.path.getsize(FILE_PROVEEDORES) == 0:
        df_p = pd.DataFrame(columns=["Fecha", "Proveedor", "Operacion", "Debe", "Haber", "Saldo_Pendiente", "Medio_Pago"])
        df_p.to_csv(FILE_PROVEEDORES, index=False)

inicializar_archivos()

# --- INTERFAZ PRINCIPAL ---
st.title("📦 Sistema de Gestión Integral - Verdulería Mayorista")
st.sidebar.title("Menú de Navegación")
menu = st.sidebar.radio("Seleccione una sección:", [
    "1. Ingresos y Costos (Viaje Multiproducto)", 
    "2. Inventario, Stock y Edición", 
    "3. Nueva Venta / Remito", 
    "4. Cuentas Corrientes Clientes", 
    "5. Cuentas Corrientes Proveedores", 
    "6. Balances y Reportes"
])

# ==========================================
# SECCIÓN 1: INGRESOS Y COSTOS (MULTIPRODUCTO)
# ==========================================
if menu == "1. Ingresos y Costos (Viaje Multiproducto)":
    st.header("🚛 Ingreso de Viaje con Múltiples Productos")
    st.write("Configura los gastos generales del transporte y añade los productos seleccionando de tu historial o creando nuevos.")

    if "viaje_items" not in st.session_state:
        st.session_state.viaje_items = []

    try:
        df_inv_hist = pd.read_csv(FILE_INVENTARIO)
    except:
        df_inv_hist = pd.DataFrame()

    try:
        df_prov_hist = pd.read_csv(FILE_PROVEEDORES)
    except:
        df_prov_hist = pd.DataFrame()
    
    lista_productos_existentes = sorted(df_inv_hist["Producto"].dropna().unique().tolist()) if not df_inv_hist.empty and "Producto" in df_inv_hist.columns else []
    lista_proveedores_existentes = sorted(df_prov_hist["Proveedor"].dropna().unique().tolist()) if not df_prov_hist.empty and "Proveedor" in df_prov_hist.columns else []

    with st.form("form_gastos_viaje"):
        st.subheader("🚚 1. Costos Generales del Transporte (Viaje)")
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            fecha_viaje = st.date_input("Fecha del Viaje", value=datetime.now())
            tipo_logistica = st.selectbox("Tipo de Vehículo / Flete", [
                "Camioneta Propia (Gasoil + Chofer + Entrada)", 
                "Camión Tercerizado - Chasis", 
                "Camión Tercerizado - Semirremolque",
                "Retiro en Origen / Sin Flete"
            ])
            
            if len(lista_proveedores_existentes) > 0:
                opciones_prov = lista_proveedores_existentes + ["Nuevo proveedor..."]
                prov_select = st.selectbox("Proveedor Principal del Viaje", opciones_prov)
                if prov_select == "Nuevo proveedor...":
                    proveedor_general = st.text_input("Ingrese el nombre del nuevo proveedor")
                else:
                    proveedor_general = prov_select
            else:
                proveedor_general = st.text_input("Nombre del Proveedor Principal")

        with col_g2:
            if "Camioneta Propia" in tipo_logistica:
                gasoil = st.number_input("Costo Total Gasoil ($)", min_value=0.0, step=100.0, value=0.0)
                sueldo_chofer = st.number_input("Sueldo / Viático chofer ($)", min_value=0.0, step=100.0, value=0.0)
                entrada_feria = st.number_input("Arancel Entrada Feria ($)", min_value=0.0, step=100.0, value=0.0)
                costo_general_viaje = gasoil + sueldo_chofer + entrada_feria
            elif "Camión Tercerizado" in tipo_logistica:
                flete_tercero = st.number_input("Costo Total del Flete ($)", min_value=0.0, step=100.0, value=0.0)
                entrada_feria = st.number_input("Arancel Entrada Feria ($)", min_value=0.0, step=100.0, value=0.0)
                costo_general_viaje = flete_tercero + entrada_feria
            else:
                entrada_feria = st.number_input("Arancel Entrada Feria ($)", min_value=0.0, step=100.0, value=0.0)
                costo_general_viaje = entrada_feria
        
        st.form_submit_button("Guardar configuración general del viaje")

    st.markdown("---")
    st.subheader("📦 2. Agregar Productos de este Viaje")
    
    with st.form("form_agregar_item_lista", clear_on_submit=True):
        col_i1, col_i2 = st.columns(2)
        
        with col_i1:
            if len(lista_productos_existentes) > 0:
                opciones_prod = lista_productos_existentes + ["Nuevo producto..."]
                prod_eleccion = st.selectbox("Seleccionar Producto", opciones_prod)
                if prod_eleccion == "Nuevo producto...":
                    i_nombre = st.text_input("Nombre del nuevo producto (Ej: Tomate 1era grande)")
                else:
                    i_nombre = prod_eleccion
            else:
                i_nombre = st.text_input("Nombre del Producto (Ej: Tomate 1era grande)")

            i_bultos = st.number_input("Cantidad de Bultos", min_value=1, step=1, value=1)

        with col_i2:
            i_proveedor = st.text_input("Proveedor específico de este ítem", value=proveedor_general)
            i_costo = st.number_input("Costo Unitario de Compra ($)", min_value=0.0, step=10.0)
            i_descarga = st.number_input("Costo de Descarga Específica (ej. autoelevador) ($)", min_value=0.0, step=10.0, value=0.0)
        
        btn_sumar = st.form_submit_button("Añadir a la lista del viaje")
        if btn_sumar:
            producto_final = i_nombre if isinstance(i_nombre, str) else prod_eleccion
            if str(producto_final).strip() == "" or str(i_proveedor).strip() == "":
                st.error("Completa el nombre del producto y el proveedor.")
            else:
                st.session_state.viaje_items.append({
                    "Producto": str(producto_final).strip(),
                    "Proveedor": str(i_proveedor).strip(),
                    "Bultos": i_bultos,
                    "Costo_Unitario": i_costo,
                    "Descarga_Especifica": i_descarga
                })
                st.success(f"¡Agregado: {i_bultos}x {str(producto_final).strip()} ({str(i_proveedor).strip()})!")

    if len(st.session_state.viaje_items) > 0:
        st.markdown("---")
        st.subheader("📋 Productos cargados en este Viaje (Pendientes de Confirmar)")
        df_viaje_temp = pd.DataFrame(st.session_state.viaje_items)
        st.dataframe(df_viaje_temp, use_container_width=True)

        total_bultos_viaje = df_viaje_temp["Bultos"].sum()
        total_monto_compra_mercaderia = (df_viaje_temp["Bultos"] * df_viaje_temp["Costo_Unitario"]).sum()
        st.info(f"📦 Total de bultos: **{total_bultos_viaje}** | 💰 Total Compra Mercadería: **${total_monto_compra_mercaderia:,.2f}**")

        col_acc1, col_acc2 = st.columns(2)
        
        with col_acc1:
            if st.button("🚀 Confirmar Viaje Completo y Registrar en Inventario"):
                costo_general_total = locals().get("costo_general_viaje", 0.0)
                gasto_logistica_por_bulto = costo_general_total / total_bultos_viaje if total_bultos_viaje > 0 else 0

                df_inv = pd.read_csv(FILE_INVENTARIO)
                nuevo_id_base = int(df_inv["ID"].max() + 1) if not df_inv.empty and "ID" in df_inv.columns else 1
                if pd.isna(nuevo_id_base): nuevo_id_base = 1

                nuevos_lotes = []
                for idx, item in enumerate(st.session_state.viaje_items):
                    b = item["Bultos"]
                    c_unit = item["Costo_Unitario"]
                    descarga_bulto = item["Descarga_Especifica"] / b if b > 0 else 0
                    
                    costo_final = c_unit + gasto_logistica_por_bulto + descarga_bulto

                    nuevos_lotes.append({
                        "ID": nuevo_id_base + idx,
                        "Fecha_Ingreso": str(fecha_viaje),
                        "Producto": item["Producto"],
                        "Proveedor": item["Proveedor"],
                        "Bultos_Ingresados": b,
                        "Costo_Unitario": c_unit,
                        "Costo_Logistica_Prorrateo": gasto_logistica_por_bulto + descarga_bulto,
                        "Costo_Final_Unitario": costo_final,
                        "Stock_Actual": b,
                        "Tipo_Logistica": tipo_logistica,
                        "Estado": "Activo"
                    })

                df_nuevos = pd.DataFrame(nuevos_lotes)
                df_inv = pd.concat([df_inv, df_nuevos], ignore_index=True)
                df_inv.to_csv(FILE_INVENTARIO, index=False)

                df_prov = pd.read_csv(FILE_PROVEEDORES)
                compras_por_proveedor = df_viaje_temp.groupby("Proveedor").apply(lambda x: (x["Bultos"] * x["Costo_Unitario"]).sum()).reset_index(name="Monto_Compra")
                
                nuevas_deudas_prov = []
                for _, row_prov in compras_por_proveedor.iterrows():
                    p_nombre = row_prov["Proveedor"]
                    p_monto = row_prov["Monto_Compra"]
                    
                    if p_monto > 0:
                        nuevas_deudas_prov.append({
                            "Fecha": str(fecha_viaje),
                            "Proveedor": p_nombre,
                            "Operacion": f"Compra de mercadería (Viaje {fecha_viaje})",
                            "Debe": p_monto,
                            "Haber": 0.0,
                            "Saldo_Pendiente": p_monto,
                            "Medio_Pago": "Cuenta Corriente"
                        })

                if len(nuevas_deudas_prov) > 0:
                    df_nuevas_deudas = pd.DataFrame(nuevas_deudas_prov)
                    df_prov = pd.concat([df_prov, df_nuevas_deudas], ignore_index=True)
                    df_prov.to_csv(FILE_PROVEEDORES, index=False)

                st.success("¡Viaje registrado con éxito en Inventario y Cuentas Corrientes de Proveedores!")
                st.session_state.viaje_items = []
                st.rerun()

        with col_acc2:
            if st.button("🗑️ Vaciar lista del viaje"):
                st.session_state.viaje_items = []
                st.rerun()

    st.markdown("---")
    st.subheader("📋 Inventario General Actual")
    try:
        df_inv_actual = pd.read_csv(FILE_INVENTARIO)
        if not df_inv_actual.empty:
            st.dataframe(df_inv_actual, use_container_width=True)
        else:
            st.info("No hay inventario cargado.")
    except:
        st.info("No hay inventario cargado.")

# ==========================================
# SECCIÓN 2: INVENTARIO, STOCK Y EDICIÓN
# ==========================================
elif menu == "2. Inventario, Stock y Edición":
    st.header("📦 Control de Existencias, Mermas y Estadísticas de Ingreso")
    try:
        df_inv = pd.read_csv(FILE_INVENTARIO)
    except:
        df_inv = pd.DataFrame()

    if not df_inv.empty and "ID" in df_inv.columns:
        st.subheader("📊 Frecuencia e Ingresos Totales por Producto")
        df_stats = df_inv.groupby("Producto")["Bultos_Ingresados"].sum().reset_index().rename(columns={"Bultos_Ingresados": "Total_Bultos_Historico"})
        st.dataframe(df_stats, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📋 Lotes Detallados en Inventario")
        st.dataframe(df_inv, use_container_width=True)
        
        st.markdown("---")
        col_m1, col_m2 = st.columns(2)

        with col_m1:
            st.subheader("⚠️ Registrar Merma / Pérdida")
            with st.form("form_merma"):
                lote_id_m = st.selectbox("ID de Lote a Descontar", df_inv["ID"].tolist())
                bultos_merma = st.number_input("Cantidad de Bultos Perdidos", min_value=1, step=1)
                btn_merma = st.form_submit_button("Aplicar Merma")

                if btn_merma:
                    idx = df_inv[df_inv["ID"] == lote_id_m].index[0]
                    if df_inv.loc[idx, "Stock_Actual"] >= bultos_merma:
                        df_inv.loc[idx, "Stock_Actual"] -= bultos_merma
                        df_inv.to_csv(FILE_INVENTARIO, index=False)
                        st.success("Merma descontada correctamente.")
                        st.rerun()
                    else:
                        st.error("No hay suficiente stock.")

        with col_m2:
            st.subheader("❌ Eliminar Lote Erróneo")
            with st.form("form_borrar_lote"):
                lote_id_b = st.selectbox("ID de Lote a Eliminar", df_inv["ID"].tolist(), key="del_lote")
                btn_borrar = st.form_submit_button("Eliminar Lote")

                if btn_borrar:
                    df_inv = df_inv[df_inv["ID"] != lote_id_b]
                    df_inv.to_csv(FILE_INVENTARIO, index=False)
                    st.warning("Lote eliminado.")
                    st.rerun()
    else:
        st.info("No hay inventario cargado.")

# ==========================================
# SECCIÓN 3: NUEVA VENTA / REMITO
# ==========================================
elif menu == "3. Nueva Venta / Remito":
    st.header("📝 Emisión de Remito / Nota de Pedido")
    try:
        df_inv = pd.read_csv(FILE_INVENTARIO)
    except:
        df_inv = pd.DataFrame()

    try:
        df_ventas = pd.read_csv(FILE_VENTAS)
    except:
        df_ventas = pd.DataFrame()

    if df_inv.empty or "Stock_Actual" not in df_inv.columns:
        st.warning("Primero debes cargar mercadería en la sección 1.")
    else:
        tipo_cliente = st.radio("Tipo de Operación:", ["Consumidor Final", "Cuenta Corriente"])
        
        try:
            df_cli_hist = pd.read_csv(FILE_CLIENTES)
            lista_clientes = sorted(df_cli_hist["Cliente"].dropna().unique().tolist()) if not df_cli_hist.empty and "Cliente" in df_cli_hist.columns else []
        except:
            lista_clientes = []

        if tipo_cliente == "Cuenta Corriente":
            if len(lista_clientes) > 0:
                opciones_cli = lista_clientes + ["Nuevo cliente..."]
                cli_select = st.selectbox("Cliente", opciones_cli)
                if cli_select == "Nuevo cliente...":
                    cliente = st.text_input("Nombre del nuevo cliente")
                else:
                    cliente = cli_select
            else:
                cliente = st.text_input("Nombre / Razón Social del Cliente")
        else:
            cliente = "Particular"
        
        st.markdown("---")
        st.subheader("🛒 Agregar Productos al Pedido")

        productos_disponibles = df_inv[df_inv["Stock_Actual"] > 0]
        
        if "carrito" not in st.session_state:
            st.session_state.carrito = []

        with st.form("form_item_carrito", clear_on_submit=True):
            prod_seleccionado = st.selectbox("Producto", productos_disponibles["Producto"].tolist() if not productos_disponibles.empty else [])
            
            if prod_seleccionado:
                lote_match = productos_disponibles[productos_disponibles["Producto"] == prod_seleccionado].iloc[0]
                costo_ref = lote_match["Costo_Final_Unitario"]
                stock_disp = lote_match["Stock_Actual"]
                id_lote_sel = lote_match["ID"]
                st.info(f"💡 Costo Final Real: **${costo_ref:,.2f}** por bulto | Stock Disponible: **{stock_disp} bultos**")
            else:
                costo_ref = 0.0
                stock_disp = 0
                id_lote_sel = None

            cant_bultos = st.number_input("Cantidad de Bultos a Vender", min_value=1, max_value=int(stock_disp) if stock_disp > 0 else 1, step=1, value=1)
            precio_venta = st.number_input("Precio de Venta Unitario ($)", min_value=0.0, step=10.0)
            
            add_item = st.form_submit_button("Agregar al Carrito")
            
            if add_item:
                subtotal = cant_bultos * precio_venta
                costo_total_item = cant_bultos * costo_ref
                st.session_state.carrito.append({
                    "ID_Lote": id_lote_sel,
                    "Producto": prod_seleccionado,
                    "Bultos": cant_bultos,
                    "Costo_Unit": costo_ref,
                    "Costo_Total_Item": costo_total_item,
                    "Precio_Unit": precio_venta,
                    "Subtotal": subtotal
                })
                st.success("Ítem agregado.")

        if len(st.session_state.carrito) > 0:
            st.subheader("📋 Detalle del Pedido Actual")
            df_carrito = pd.DataFrame(st.session_state.carrito)
            st.dataframe(df_carrito[["Producto", "Bultos", "Precio_Unit", "Subtotal"]], use_container_width=True)

            total_general = df_carrito["Subtotal"].sum()
            total_costo_cmv = df_carrito["Costo_Total_Item"].sum()
            total_bultos_gral = df_carrito["Bultos"].sum()
            
            st.markdown(f"### 💵 Total General del Pedido: **${total_general:,.2f}** (Costo Original CMV: ${total_costo_cmv:,.2f} | Bultos: {total_bultos_gral})")

            medio_pago = st.selectbox("Medio de Pago", ["Efectivo", "Transferencia", "Echeq", "Cuenta Corriente"])

            if st.button("🚀 Confirmar y Registrar Venta"):
                for item in st.session_state.carrito:
                    l_id = item["ID_Lote"]
                    b_vendidos = item["Bultos"]
                    idx_inv = df_inv[df_inv["ID"] == l_id].index
                    if not idx_inv.empty:
                        df_inv.loc[idx_inv[0], "Stock_Actual"] -= b_vendidos
                df_inv.to_csv(FILE_INVENTARIO, index=False)

                nuevo_id_v = int(df_ventas["ID_Venta"].max() + 1) if not df_ventas.empty and "ID_Venta" in df_ventas.columns else 1
                if pd.isna(nuevo_id_v): nuevo_id_v = 1
                
                detalle_txt = " - ".join([f"{row['Bultos']}x {row['Producto']}" for row in st.session_state.carrito])
                
                nueva_venta = pd.DataFrame({
                    "ID_Venta": [nuevo_id_v],
                    "Fecha": [datetime.now().strftime("%Y-%m-%d %H:%M")],
                    "Cliente": [cliente],
                    "Tipo_Cliente": [tipo_cliente],
                    "Detalle_Items": [detalle_txt],
                    "Total_Bultos": [total_bultos_gral],
                    "Monto_Total": [total_general],
                    "Costo_CMV": [total_costo_cmv],
                    "Medio_Pago": [medio_pago if tipo_cliente=="Consumidor Final" else "Cuenta Corriente"],
                    "Estado_Pago": ["Pagado" if tipo_cliente=="Consumidor Final" else "Fiado Pendiente"]
                })
                df_ventas = pd.concat([df_ventas, nueva_venta], ignore_index=True)
                df_ventas.to_csv
