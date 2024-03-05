import json
import pysam
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def extract_query_params(event):
    query_params = event.get('queryStringParameters')
    if not query_params:
        logger.error("No query string parameters provided.")

        return None

    chromosome = query_params.get('chromosome')
    start = query_params.get('start')
    end = query_params.get('end')

    if not all([chromosome, start, end]):
        logger.error("Incomplete query string parameters.")

        return None

    try:
        start, end = int(start), int(end)
    except ValueError:
        logger.error("Invalid query parameter format.")

        return None

    return chromosome, start, end

def process_vcf_file(vcf_file_path, chromosome, start, end):
    try:
        logger.info(f"Processing VCF file: {vcf_file_path} for chromosome: {chromosome}, start: {start}, end: {end}")
        vcf = pysam.VariantFile(vcf_file_path)
        
        found_variants = [ 
            {
                "chrom": rec.chrom,
                "pos": rec.pos,
                "ref": rec.ref,
                "alt": ','.join(rec.alts)
            }
            for rec in vcf.fetch(chromosome, start, end)
        ]

        return found_variants
    
    except Exception as e:
        logger.error(f"Error processing VCF file {vcf_file_path}: {str(e)}")

        return None

def generate_response(message, variants=None, query=None):
    response_body = {
        "message": message,
        "variants": variants if variants is not None else [],
        "query": query if query is not None else {}
    }

    return {
        'statusCode': 200 if variants is not None else 500,
        'body': json.dumps(response_body)
    }

def lambda_handler(event, context):
    params = extract_query_params(event)
    if params is None:
        return generate_response('Invalid or missing query parameters')

    chromosome, start, end = params
    vcf_file_path = '/data/GATK_variants.vcf.gz'
    
    logger.info(f"Contents of /data directory: {os.listdir('/data')}")
    found_variants = process_vcf_file(vcf_file_path, chromosome, start, end)

    if found_variants is None:
        return generate_response('Error processing your request')

    message = "Variants found" if found_variants else "No variants found"

    return generate_response(message, found_variants, {"chromosome": chromosome, "start": start, "end": end})
