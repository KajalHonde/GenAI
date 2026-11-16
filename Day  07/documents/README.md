# AapdaMitra source documents

Copy the AapdaMitra emergency-preparedness and disaster-response source documents
into this folder (or its subfolders).

Supported formats:
- PDF (`.pdf`) — page numbers are retained from the PDF.
- Word (`.docx`) — treated as one logical page because printed page numbers are
  not reliably available from DOCX paragraph text.
- Text (`.txt`) and Markdown (`.md`) — page is 1 unless form-feed page breaks
  are present.

For Markdown, the first `# Heading` is used as the document title. For other
formats, the filename (or PDF metadata title) is used.

Keep original source filenames. The search index stores the relative source path,
page number and title with every chunk.
