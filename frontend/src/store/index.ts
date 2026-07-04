import { create } from 'zustand';
import type { ScanResult } from '@/types';

interface ScanState {
  currentScan: ScanResult | null;
  isScanning: boolean;
  setCurrentScan: (scan: ScanResult | null) => void;
  setIsScanning: (val: boolean) => void;
}

export const useScanStore = create<ScanState>((set) => ({
  currentScan: null,
  isScanning: false,
  setCurrentScan: (scan) => set({ currentScan: scan }),
  setIsScanning: (val) => set({ isScanning: val }),
}));
