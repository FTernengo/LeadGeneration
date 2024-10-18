require('dotenv').config();
const axios = require('axios');
const ExcelJS = require('exceljs');

const HUNTER_API_KEY = process.env.HUNTER_API_KEY;
const HUNTER_API_URL = 'https://api.hunter.io/v2/domain-search';

async function fetchLeadsFromHunter(domain, limit = 10) {
  try {
    const response = await axios.get(HUNTER_API_URL, {
      params: {
        domain: domain,
        limit: limit,
        api_key: HUNTER_API_KEY
      }
    });
    return response.data.data.emails.map(email => ({...email, domain}));
  } catch (error) {
    console.error(`Error fetching leads from Hunter for domain ${domain}:`, error.message);
    return [];
  }
}

async function saveLeadsToExcel(leads) {
  const workbook = new ExcelJS.Workbook();
  const worksheet = workbook.addWorksheet('Leads');

  worksheet.columns = [
    { header: 'First Name', key: 'first_name', width: 20 },
    { header: 'Last Name', key: 'last_name', width: 20 },
    { header: 'Email', key: 'value', width: 30 },
    { header: 'Position', key: 'position', width: 30 },
    { header: 'Company', key: 'company', width: 30 },
    { header: 'Domain', key: 'domain', width: 30 }
  ];

  worksheet.addRows(leads);

  await workbook.xlsx.writeFile('solar_leads.xlsx');
  console.log('Leads saved to solar_leads.xlsx');
}

async function generateLeads(domains, limit = 10) {
  try {
    let allLeads = [];
    for (const domain of domains) {
      console.log(`Fetching leads for ${domain}...`);
      const leads = await fetchLeadsFromHunter(domain, limit);
      allLeads = allLeads.concat(leads);
      // Añadir un pequeño retraso para evitar sobrecargar la API
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    await saveLeadsToExcel(allLeads);
    console.log('Lead generation process completed successfully');
  } catch (error) {
    console.error('Error in lead generation process:', error);
  }
}

// Lista de dominios de empresas de energía solar
const solarDomains = [
  'sunpower.com',
  'firstsolar.com',
  'jinkosolar.com',
  'canadiansolar.com',
  'trinasolar.com',
  'enphase.com',
  'solaredge.com',
  'lgcorp.com',
  'hanwha.com',
  'rec-group.com',
  'solarworld.de',
  'yinglisolar.com',
  'sma-solar.com',
  'fronius.com',
  'abb.com'
];

// Ejecutar la generación de leads
generateLeads(solarDomains, 5);