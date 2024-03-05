import unittest
from unittest.mock import patch, MagicMock
from your_lambda_file import lambda_handler

class TestLambdaFunction(unittest.TestCase):
    def setUp(self):
        self.valid_event = {
            'queryStringParameters': {
                'chromosome': 'chr1',
                'start': '100000',
                'end': '101000'
            }
        }
        self.invalid_event_missing_params = {'queryStringParameters': {}}
        self.invalid_event_bad_params = {
            'queryStringParameters': {
                'chromosome': 'chr1',
                'start': 'one hundred thousand',
                'end': 'one hundred and one thousand'
            }
        }

    @patch('your_lambda_file.os.listdir', return_value=['GATK_variants.vcf.gz'])
    @patch('your_lambda_file.pysam.VariantFile')
    def test_valid_request_with_variants(self, mock_variant_file, mock_listdir):
        # Setup mock for VariantFile
        mock_vcf = MagicMock()
        mock_vcf.fetch.return_value = [MagicMock(chrom='chr1', pos=100010, ref='A', alts=['C'])]
        mock_variant_file.return_value = mock_vcf
        
        response = lambda_handler(self.valid_event, None)
        self.assertEqual(response['statusCode'], 200)
        self.assertIn("Variants found", response['body'])

    def test_invalid_request_missing_parameters(self):
        response = lambda_handler(self.invalid_event_missing_params, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn("Invalid or missing query parameters", response['body'])

    def test_invalid_request_bad_parameters(self):
        response = lambda_handler(self.invalid_event_bad_params, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn("Invalid query parameter format", response['body'])

if __name__ == '__main__':
    unittest.main()
