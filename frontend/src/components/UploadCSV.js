import React, { useState } from "react";

function UploadCSV() {
  const [fileName, setFileName] = useState("");
  const [dataPreview, setDataPreview] = useState([]);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    setFileName(file.name);

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target.result;
      const rows = text.split("\n").map((row) => row.split(","));
      setDataPreview(rows);
    };
    reader.readAsText(file);
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>📄 Subir archivo CSV</h2>
      <input type="file" accept=".csv" onChange={handleFileUpload} />

      {fileName && (
        <p>
          Archivo seleccionado: <strong>{fileName}</strong>
        </p>
      )}

      <h3>Vista previa del CSV:</h3>
      <table border="1" cellPadding="5">
        <tbody>
          {dataPreview.slice(0, 5).map((row, rowIndex) => (
            <tr key={rowIndex}>
              {row.map((column, colIndex) => (
                <td key={colIndex}>{column}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <p>(Se muestran solo las primeras 5 filas)</p>
    </div>
  );
}

export default UploadCSV;
