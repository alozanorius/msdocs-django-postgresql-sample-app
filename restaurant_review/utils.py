import pypdf
import xlwt
from io import BytesIO

def lee_correo_pdf(filename):
    #with open(filename, 'rb') as file:
    reader = pypdf.PdfReader(filename)
    texto_en_paginas = []
    for page in reader.pages:
            texto_en_paginas.append(page.extract_text())
    return texto_en_paginas

## Junta últimas 2 páginas
def junta_ultimas_2(lista_paginas_texto):
    pag1, pag2 = lista_paginas_texto[1], lista_paginas_texto[2]
    texto_a_buscar = "dirígete a tu Bandeja de entrada en la computadora.\n\u200a\n \n\u200a\n"
    ind_final2 =  pag2.find(texto_a_buscar)
    texto_final_2 = pag2[(ind_final2+len(texto_a_buscar)):-3]
    # print(texto_final_2)
    pag1 = pag1[:pag1.find(texto_final_2)]
    pag1y2 = pag1 + "\n" + pag2
    lista_paginas_texto[1] = pag1y2
    lista_paginas_texto.pop()
    return lista_paginas_texto


def retorna_listado_parser():
    listado_parser = [ 
        ("I", "Siniestro", 0, "bajo el no. de atención", "."),
        ("II", "Tramitador", 0, "", ""),
        ("II", "Liquidador Asignado", 0, "BECKETT S.A. LIQUIDADORES DE SEGUROS", ""),
        ("II", "Num Póliza", 0, 20103672, ""),
        ("II", "Ncertif", 0, 1, ""),
        ("I", "Tipo Siniestro", 1, "Tipo de denuncia (robo o incendio):", "\n"),
        ("III", "Causal Siniestro", 0, 0, 0),
        ("I", "Nombre Asegurado", 1, "Nombre completo / Razón Social del asegurado:", "\nRut del asegurado"),
        ("I", "Rut Asegurado", 1, "Rut del asegurado:", "\n"),
        ("I", "Dirección", 1, "Dirección donde ocurrió el evento:", "\n"),    
        ("I", "Comuna", 1, "Comuna:", "\n"),
        ("I", "Region", 1, "Región:", "\n"),
        ("I", "Fecha Ocurrencia", 1, "Fecha del evento y hora aproximda:", "\n"),
        ("I", "Fecha Denuncio", 1, "@wixforms.com>\nEnviado el:", "\n"),
        ("I", "Fecha Asignación", 0, "@sbins.cl>\nEnviado:", "\n"),    
        ("III", "Desc. Cobertura", 0, 0, 0),
        ("I", "Nombre Contacto", 0, "contacto para liquidador:\nNombre:", "\n"),
        ("I", "Fono 1", 0, "Teléfono:", "\n"), 
        ("II", "Fono 2", 0, "", ""),
        ("I", "Email Asegurado", 0, "Correo:", "\n"), 
        ("II", "N° Operación", 0, "", ""),
        ("II", "N° SIAC", 0, "", ""), 
        ("II", "N° SAS / N° Siniestro Líder", 0, "", ""), 
        ("II", "N° MUS", 0, "", ""), 
        ("II", "Monto Asegurado", 0, 100, ""), 
        ("II", "Asesor", 0, "", ""), 
        ("I", "Breve Descripción", 1, "Relato breve de los hechos:", "\nMonto estimado de la perdida"),
        ]
    return listado_parser

def extrae_info_estructurada(texto_en_lista, listado_parser):
    datos_extraidos_dict = dict()
    for parse in listado_parser:
        (tipo, campo, pagina, text_ant, text_fin) = parse
        #print(campo)
        if tipo == "I":
            if (text_ant in texto_en_lista[pagina]):
                ind_inicio = texto_en_lista[pagina].find(text_ant) + len(text_ant)
                if (text_fin in (texto_en_lista[pagina])[ind_inicio:]):
                    ind_final = ((texto_en_lista[pagina][ind_inicio:]).find(text_fin) + ind_inicio)
                    texto = (texto_en_lista[pagina][ind_inicio:ind_final]).strip().replace("\n", " ")
                    datos_extraidos_dict[campo]= texto
                    #print(f"{campo}:     {texto}") 
                else:
                    raise IndexError(f"En el campo '{campo}', el fin de texto '{text_fin}' no existe.")
            else:
                raise IndexError(f"En el campo '{campo}', el inicio de texto '{text_ant}' no existe.")
        elif tipo == "II":
            texto = text_ant
            datos_extraidos_dict[campo]= texto
        elif tipo == "III":
            tipo_siniestro = datos_extraidos_dict["Tipo Siniestro"]
            if campo == "Causal Siniestro":
                if tipo_siniestro == "Robo":
                   datos_extraidos_dict[campo]= "Robo con fuerza en las cosas"
                else:
                   datos_extraidos_dict[campo]= "Incendio"
            elif campo == "Desc. Cobertura":
                if tipo_siniestro == "Robo":
                   datos_extraidos_dict[campo]= "POL120130697"
                else:
                   datos_extraidos_dict[campo]= "POL120130178"              
    return datos_extraidos_dict

def extraccion_total(archivo):
    texto_en_paginas = lee_correo_pdf(archivo)
    texto_en_paginas = junta_ultimas_2(texto_en_paginas)
    listado_parser = retorna_listado_parser()
    datos_extraidos = extrae_info_estructurada(texto_en_paginas, listado_parser)
    return (datos_extraidos)

def crear_excel_xls_con_archivo(datos_lista, nombre_archivo_salida):
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Información de Siniestros')

    # Establecer las cabeceras (claves del primer diccionario)
    if datos_lista:
        cabeceras = list(datos_lista[0].keys())
        for col_index, cabecera in enumerate(cabeceras):
            ws.write(0, col_index, cabecera)

        # Agregar los datos de cada diccionario como una nueva fila
        for row_index, datos in enumerate(datos_lista, start=1):
            for col_index, cabecera in enumerate(cabeceras):
                valor = datos.get(cabecera, "")
                if cabecera == "Siniestro" or cabecera == "Fono 1":
                    try:
                        valor = int(valor)  # Intentar convertir a entero si es la columna 'Siniestro'
                    except ValueError:
                        pass
                ws.write(row_index, col_index, valor)

    # Guardar el archivo en un objeto BytesIO
    response_stream = BytesIO()
    wb.save(response_stream)
    response_stream.seek(0)
    return (response_stream)

    # Configurar la respuesta HTTP con el tipo MIME adecuado
    #response = HttpResponse(response_stream.getvalue(), content_type='application/vnd.ms-excel')
    #response['Content-Disposition'] = 'attachment; filename="datos_de_muestra.xls"'

    #return response

    # Guardar el archivo Excel
    #wb.save(f"{nombre_archivo_salida}.xls")

