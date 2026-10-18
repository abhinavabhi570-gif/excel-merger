from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
import pandas as pd
import io
import os
import tempfile

app = FastAPI()

# 1. http://localhost:8000 തുറക്കുമ്പോൾ വെബ് പേജ് കാണിക്കാൻ
@app.get("/", response_class=HTMLResponse)
async def serve_home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# 2. ഫയലുകൾ അപ്‌ലോഡ് ചെയ്ത്, സംയോജിപ്പിച്ച്, ഡൗൺലോഡ് ചെയ്യാൻ നൽകുന്നു
@app.post("/merge")
async def merge_files(files: list[UploadFile] = File(...)):
    combined_dfs = []

    for file in files:
        # ഫയൽ മെമ്മറിയിലേക്ക് റീഡ് ചെയ്യുന്നു
        content = await file.read()
        
        # openpyxl ഉപയോഗിച്ച് ആദ്യത്തെ ഷീറ്റ് വായിക്കുന്നു
        df = pd.read_excel(io.BytesIO(content), engine="openpyxl")
        
        # ഏത് ഫയലിലെ ഡാറ്റയാണെന്ന് തിരിച്ചറിയാൻ ഫയലിന്റെ പേര് ഒരു കോളമായി ചേർക്കുന്നു
        df["Source_File"] = file.filename
        combined_dfs.append(df)

    # എല്ലാ ഷീറ്റുകളും ഒന്നിന് താഴെ ഒന്നായി സംയോജിപ്പിക്കുന്നു
    merged_df = pd.concat(combined_dfs, ignore_index=True)

    # താല്ക്കാലിക Excel ഫയലിലേക്ക് സേവ് ചെയ്യുന്നു
    temp_dir = tempfile.gettempdir()
    output_path = os.path.join(temp_dir, "merged_output.xlsx")
    merged_df.to_excel(output_path, index=False, engine="openpyxl")

    # ഡൗൺലോഡിനായി ഫയൽ തിരികെ അയക്കുന്നു
    return FileResponse(
        path=output_path,
        filename="merged_output.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)