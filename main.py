from tl_idf import make_matrices
from scraper import *

if __name__ == "__main__":
	q = yahoo_boss_request("learn python", 20)
	page_infos = extract_info_from_yahoo_response(q)
	htmls = extract_html_from_urls([x['url'] for x in page_infos])

	make_matrices(zip(page_infos, htmls))