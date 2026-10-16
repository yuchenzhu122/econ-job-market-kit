import PDFKit
let d = PDFDocument(url: URL(fileURLWithPath: CommandLine.arguments[1]))!
print("PAGES: \(d.pageCount)")
if d.pageCount > 1 { for i in 1..<d.pageCount { print("--- page \(i+1):"); print(d.page(at: i)!.string ?? "") } }
