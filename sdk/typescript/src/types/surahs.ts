
export interface SurahsListResponseData {
    count: number;
    next?: string;
    previous?: string;
    results: object[];
}
export interface SurahsListRequestParams {
    limit?: number;
    mushaf: string;
    offset?: number;
    ordering?: string;
    search?: string;
}
export interface SurahsCreateRequestData {
    bismillah: string;
    mushaf: object;
    mushaf_uuid: string;
    name: string;
    names: string;
    number: number;
    number_of_ayahs: string;
    period?: 'makki' | 'madani';
    search_terms?: string;
    uuid: string;
}
export interface SurahsCreateResponseData {
    bismillah: string;
    mushaf: object;
    mushaf_uuid: string;
    name: string;
    names: string;
    number: number;
    number_of_ayahs: string;
    period?: 'makki' | 'madani';
    search_terms?: string;
    uuid: string;
}
export interface SurahsRetrieveResponseData {
    ayahs: object[];
    bismillah: string;
    mushaf: object;
    mushaf_uuid: string;
    name: string;
    names: string;
    number: number;
    number_of_ayahs: string;
    period?: 'makki' | 'madani';
    search_terms?: string;
    uuid: string;
}
export interface SurahsUpdateRequestData {
    bismillah: string;
    mushaf: object;
    mushaf_uuid: string;
    name: string;
    names: string;
    number: number;
    number_of_ayahs: string;
    period?: 'makki' | 'madani';
    search_terms?: string;
    uuid: string;
}
export interface SurahsUpdateResponseData {
    bismillah: string;
    mushaf: object;
    mushaf_uuid: string;
    name: string;
    names: string;
    number: number;
    number_of_ayahs: string;
    period?: 'makki' | 'madani';
    search_terms?: string;
    uuid: string;
}
export interface SurahsPartialupdateRequestData {
    bismillah?: string;
    mushaf?: object;
    mushaf_uuid?: string;
    name?: string;
    names?: string;
    number?: number;
    number_of_ayahs?: string;
    period?: 'makki' | 'madani';
    search_terms?: string;
    uuid?: string;
}
export interface SurahsPartialupdateResponseData {
    bismillah: string;
    mushaf: object;
    mushaf_uuid: string;
    name: string;
    names: string;
    number: number;
    number_of_ayahs: string;
    period?: 'makki' | 'madani';
    search_terms?: string;
    uuid: string;
}