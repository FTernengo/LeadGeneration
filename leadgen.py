import pandas as pd
import requests
from time import sleep
import os
from datetime import datetime

# Configuración
HUNTER_API_KEY = 'eec16f6de2fb62ce04b284d5043423e379ebb8ad'
INPUT_FILE = 'data/hunterDB.xlsx'
OUTPUT_FILE = f'hunter_leads_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'

def get_domain_leads(domain):
    """Obtiene todos los leads disponibles para un dominio usando la API de Hunter"""
    url = f"https://api.hunter.io/v2/domain-search"
    
    all_leads = []
    page = 1
    
    while True:
        params = {
            'domain': domain,
            'api_key': HUNTER_API_KEY,
            'page': page
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if response.status_code != 200:
                print(f"Error al procesar {domain}: {data.get('errors', ['Error desconocido'])}")
                break
                
            # Obtener leads de la página actual
            emails = data['data']['emails']
            if not emails:
                break
                
            all_leads.extend(emails)
            
            # Verificar si hay más páginas
            if page >= data['data']['meta']['total_pages']:
                break
                
            page += 1
            sleep(1)  # Pausa para respetar límites de la API
            
        except Exception as e:
            print(f"Error al procesar {domain}: {str(e)}")
            break
    
    return all_leads

def process_leads(leads, company_info):
    """Procesa los leads y añade información de la empresa"""
    processed_leads = []
    
    for lead in leads:
        lead_info = {
            'company_name': company_info['Company name'],
            'company_industry': company_info['Industry'],
            'company_location': company_info['Location'],
            'company_domain': company_info['Domain'],
            'company_linkedin': company_info['LinkedIn page'],
            'company_description': company_info['Description'],
            'email': lead.get('value', ''),
            'first_name': lead.get('first_name', ''),
            'last_name': lead.get('last_name', ''),
            'position': lead.get('position', ''),
            'seniority': lead.get('seniority', ''),
            'department': lead.get('department', ''),
            'linkedin_url': lead.get('linkedin_url', ''),
            'twitter': lead.get('twitter', ''),
            'phone_number': lead.get('phone_number', ''),
            'confidence_score': lead.get('confidence', ''),
            'verification_status': lead.get('verification.status', ''),
            'verification_date': lead.get('verification.date', '')
        }
        processed_leads.append(lead_info)
    
    return processed_leads

def main():
    # Leer archivo de empresas
    try:
        df = pd.read_csv(INPUT_FILE) if INPUT_FILE.endswith('.csv') else pd.read_excel(INPUT_FILE)
    except Exception as e:
        print(f"Error al leer el archivo: {str(e)}")
        return

    all_processed_leads = []
    
    # Procesar cada dominio
    for index, row in df.iterrows():
        print(f"Procesando {row['Domain']}...")
        
        # Obtener leads del dominio
        leads = get_domain_leads(row['Domain'])
        
        # Procesar y añadir información de la empresa
        if leads:
            processed_leads = process_leads(leads, row)
            all_processed_leads.extend(processed_leads)
            print(f"Se encontraron {len(leads)} leads para {row['Domain']}")
        else:
            print(f"No se encontraron leads para {row['Domain']}")
        
        sleep(1)  # Pausa entre dominios

    # Crear DataFrame con todos los leads
    if all_processed_leads:
        leads_df = pd.DataFrame(all_processed_leads)
        
        # Guardar resultados
        leads_df.to_excel(OUTPUT_FILE, index=False)
        print(f"\nProceso completado. Se guardaron {len(all_processed_leads)} leads en {OUTPUT_FILE}")
    else:
        print("\nNo se encontraron leads para ninguna empresa")

if __name__ == "__main__":
    main()