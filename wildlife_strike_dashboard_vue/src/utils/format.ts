import type { RiskLevel } from "../types";

export function fmtCount(value: number | undefined): string {
  return Number(value ?? 0).toLocaleString("en-US");
}

export function fmtPct(value: number | undefined, digits = 1): string {
  return `${((value ?? 0) * 100).toFixed(digits)}%`;
}

export function fmtLift(value: number | undefined): string {
  return `${(value ?? 0).toFixed(2)}x`;
}

export function riskLevel(rate: number): RiskLevel {
  if (rate >= 0.2) return "Critical";
  if (rate >= 0.1) return "High";
  if (rate >= 0.05) return "Moderate";
  return "Low";
}

export function riskColor(rate: number): string {
  const level = riskLevel(rate);
  if (level === "Critical") return "#ff5c5c";
  if (level === "High") return "#ffb84d";
  if (level === "Moderate") return "#f3d34a";
  return "#54d19a";
}
