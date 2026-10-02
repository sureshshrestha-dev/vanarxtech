import re
import io
import uuid
from typing import List, Dict, Any
from pypdf import PdfReader
from src.config import CHUNK_SIZE, CHUNK_OVERLAP


import fitz  # PyMuPDF


def detect_hidden_spans(file_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Scan PDF bytes for hidden text steganography:
    - White font on white background (color == 0xFFFFFF / 16777215)
    - Micro-fonts (font size < 2.0pt)
    - Off-page rendering (bbox outside visible page bounds)
    """
    hidden_findings = []
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page_idx, page in enumerate(doc):
            p_width = page.rect.width
            p_height = page.rect.height
            for block in page.get_text("dict").get("blocks", []):
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        color = span.get("color", 0)
                        size = span.get("size", 12)
                        bbox = span.get("bbox", (0, 0, 0, 0))

                        # Check bounding box off-page positioning
                        x0, y0, x1, y1 = bbox[0], bbox[1], bbox[2], bbox[3]
                        is_off_page = x0 < 0 or y0 < 0 or x1 > (p_width + 10) or y1 > (p_height + 10)

                        if (color in (0xFFFFFF, 16777215) or size < 2.0 or is_off_page) and text:
                            hidden_findings.append({
                                "page": page_idx + 1,
                                "text": text,
                                "color": hex(color),
                                "size": size,
                                "off_page": is_off_page
                            })
    except Exception as e:
        print(f"Steganography scan warning: {e}")
    return hidden_findings


def extract_pages_from_pdf(file_bytes: bytes, filename: str):
    """Read a PDF and return a list of pages with their text content."""
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = []

    for page_number, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()

        # Only keep pages that actually have text
        if text:
            pages.append({
                "page": page_number + 1,
                "text": text
            })

    return pages


def extract_structured_qa_pairs(pages_data: List[Dict[str, Any]]):
    """
    Try to find question-and-answer patterns in the PDF text.
    
    Looks for patterns like:
    - 1. Question text
    - Q1. Question text
    - Question 1: Question text
    - a) Option text
    
    Works across page boundaries so a Q&A that spans two pages stays together.
    """
    qa_chunks = []

    # First, join all pages into one big string but keep track of which
    # character positions belong to which page number
    all_text_parts = []
    page_ranges = []  # stores (start_index, end_index, page_number) for each page

    for page_info in pages_data:
        page_num = page_info["page"]
        text = page_info["text"]
        start = len("".join(all_text_parts))
        all_text_parts.append(text + "\n\n")
        end = len("".join(all_text_parts))
        page_ranges.append((start, end, page_num))

    full_text = "".join(all_text_parts)

    def find_page_for_position(position: int):
        """Given a character position, figure out which page it belongs to."""
        for start, end, page_num in page_ranges:
            if start <= position <= end:
                return page_num
        # If we can't find it, just return the last page
        if page_ranges:
            return page_ranges[-1][2]
        return 1

    # This regex matches common question numbering at the start of a line
    qa_pattern = re.compile(
        r'(?m)^(?:Q\d+[\.:]|Question\s*\d+[\.:]|\d+[\.\)]|\([a-z0-9]+\)|[a-z]\))\s+',
        re.IGNORECASE
    )

    # This regex finds where the answer starts (like "Answer:", "Ans:", "A1:", etc.)
    answer_pattern = re.compile(
        r'(?:\n\s*(?:Answer\s*\d*[\.:]+\s*|Ans[\.:=>\s]+|A\d*[\.:]+\s*))',
        re.IGNORECASE
    )

    matches = list(qa_pattern.finditer(full_text))

    # We need at least 2 matches to consider this a structured Q&A document
    if len(matches) >= 2:
        for i in range(len(matches)):
            # Each question goes from its match start to the next question's start
            start_pos = matches[i].start()
            if i + 1 < len(matches):
                end_pos = matches[i + 1].start()
            else:
                end_pos = len(full_text)

            chunk_text = full_text[start_pos:end_pos].strip()

            if not chunk_text:
                continue

            start_page = find_page_for_position(start_pos)
            end_page = find_page_for_position(end_pos - 1)

            # Try to split the chunk into question and answer parts
            question_text = ""
            answer_text = ""
            answer_match = answer_pattern.search(chunk_text)

            if answer_match:
                question_text = chunk_text[:answer_match.start()].strip()
                answer_text = chunk_text[answer_match.end():].strip()
            else:
                # If no answer marker found, treat first line as question and rest as answer
                lines = chunk_text.split("\n", 1)
                question_text = lines[0].strip()
                answer_text = lines[1].strip() if len(lines) > 1 else ""

            qa_chunks.append({
                "content": chunk_text,
                "question": question_text,
                "answer": answer_text,
                "page": start_page,
                "end_page": end_page,
                "is_structured_qa": True
            })

    return qa_chunks


def recursive_chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    """
    Split text into smaller chunks that fit within the chunk_size limit.
    
    Tries to split on natural boundaries first:
    1. Double newlines (paragraphs)
    2. Single newlines
    3. Sentences (period + space)
    4. Words (spaces)
    5. Individual characters (last resort)
    
    Adds overlap between chunks so context isn't lost at boundaries.
    """
    # If the text is already small enough, just return it as-is
    if len(text) <= chunk_size:
        return [text] if text else []

    # Pick the best separator to split on
    separators = ["\n\n", "\n", ". ", " ", ""]
    chosen_separator = ""
    for sep in separators:
        if sep in text:
            chosen_separator = sep
            break

    # Split the text using the chosen separator
    if chosen_separator:
        parts = text.split(chosen_separator)
    else:
        parts = list(text)

    chunks = []
    current_parts = []
    current_length = 0

    for part in parts:
        # Calculate how much space this part would take up
        part_length = len(part) + (len(chosen_separator) if current_parts else 0)

        # If adding this part would exceed the limit, save the current chunk
        if current_length + part_length > chunk_size and current_parts:
            chunk_string = chosen_separator.join(current_parts)
            chunks.append(chunk_string)

            # Keep some parts for overlap with the next chunk
            overlap_length = 0
            overlap_parts = []
            for old_part in reversed(current_parts):
                if overlap_length + len(old_part) <= overlap:
                    overlap_parts.insert(0, old_part)
                    overlap_length += len(old_part)
                else:
                    break

            current_parts = overlap_parts
            current_length = sum(len(p) for p in current_parts)
            if current_parts:
                current_length += len(chosen_separator) * (len(current_parts) - 1)

        current_parts.append(part)
        current_length += part_length

    # Don't forget the last chunk
    if current_parts:
        chunk_string = chosen_separator.join(current_parts)
        if chunk_string and (not chunks or chunks[-1] != chunk_string):
            chunks.append(chunk_string)

    return chunks


def process_pdf_document(file_bytes: bytes, filename: str, document_id: str):
    """
    Main function to process an uploaded PDF.
    
    Steps:
    1. Extract text from each page
    2. Try to detect structured Q&A patterns (like exam questions)
    3. If no Q&A patterns found, fall back to splitting pages into smaller chunks
    
    Returns a dictionary with document info and all the text chunks.
    """
    # Step 1: Get text from each page
    pages = extract_pages_from_pdf(file_bytes, filename)
    all_chunks = []

    # Step 2: Try structured Q&A extraction first
    qa_chunks = extract_structured_qa_pairs(pages)

    if qa_chunks:
        # We found Q&A patterns, use those as chunks
        for index, item in enumerate(qa_chunks):
            chunk_id = f"{document_id}_qa_{index + 1}"
            all_chunks.append({
                "chunk_id": chunk_id,
                "document_id": document_id,
                "filename": filename,
                "page": item["page"],
                "end_page": item.get("end_page", item["page"]),
                "content": item["content"],
                "question": item.get("question", ""),
                "answer": item.get("answer", ""),
                "chunk_type": "structured_qa"
            })
    else:
        # Step 3: No Q&A patterns found, split each page into smaller chunks
        for page_info in pages:
            page_num = page_info["page"]
            page_text = page_info["text"]
            text_chunks = recursive_chunk_text(page_text, CHUNK_SIZE, CHUNK_OVERLAP)

            for index, chunk_text in enumerate(text_chunks):
                chunk_id = f"{document_id}_p{page_num}_c{index + 1}"
                all_chunks.append({
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "filename": filename,
                    "page": page_num,
                    "end_page": page_num,
                    "content": chunk_text,
                    "chunk_type": "recursive_character"
                })

    return {
        "document_id": document_id,
        "filename": filename,
        "total_pages": len(pages),
        "total_chunks": len(all_chunks),
        "chunks": all_chunks
    }
