export async function loadCsv<T>(path: string): Promise<T[]> {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Unable to load ${path}`);
  }
  const text = await response.text();
  return parseCsv(text) as T[];
}

export function parseCsv(text: string): Record<string, string | number>[] {
  const rows = splitRows(text.trim());
  if (rows.length === 0) return [];
  const headers = splitLine(rows[0]).map((header) => header.trim());
  return rows.slice(1).filter(Boolean).map((row) => {
    const values = splitLine(row);
    return headers.reduce<Record<string, string | number>>((record, header, index) => {
      const value = values[index] ?? "";
      const numeric = Number(value);
      record[header || "rowLabel"] = value !== "" && Number.isFinite(numeric) ? numeric : value;
      return record;
    }, {});
  });
}

function splitRows(text: string): string[] {
  const rows: string[] = [];
  let current = "";
  let quoted = false;
  for (const char of text) {
    if (char === "\"") quoted = !quoted;
    if (char === "\n" && !quoted) {
      rows.push(current.replace(/\r$/, ""));
      current = "";
    } else {
      current += char;
    }
  }
  if (current) rows.push(current.replace(/\r$/, ""));
  return rows;
}

function splitLine(line: string): string[] {
  const values: string[] = [];
  let current = "";
  let quoted = false;
  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    const next = line[index + 1];
    if (char === "\"" && quoted && next === "\"") {
      current += "\"";
      index += 1;
    } else if (char === "\"") {
      quoted = !quoted;
    } else if (char === "," && !quoted) {
      values.push(current);
      current = "";
    } else {
      current += char;
    }
  }
  values.push(current);
  return values;
}
