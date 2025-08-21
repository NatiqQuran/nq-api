
export interface AyahsListResponseData {
    count: number;
    next?: string;
    previous?: string;
    results: object[];
}
export interface AyahsListRequestParams {
    limit?: number;
    offset?: number;
    ordering?: string;
    search?: string;
    surah_uuid?: string;
}
export interface AyahsCreateRequestData {
    bismillah_text?: string;
    is_bismillah?: boolean;
    sajdah?: string;
    surah_uuid: string;
    text: string;
}
export interface AyahsCreateResponseData {
    bismillah_text?: string;
    is_bismillah?: boolean;
    sajdah?: string;
    surah_uuid: string;
    text: string;
}
export interface AyahsRetrieveResponseData {
    bismillah: string;
    breakers: string;
    mushaf: string;
    number: number;
    sajdah?: any;
    surah: object;
    text: string;
    uuid: string;
    words: object[];
}
export interface AyahsUpdateRequestData {
    bismillah: string;
    breakers: string;
    number: number;
    sajdah?: any;
    surah: string;
    text: string;
    uuid: string;
}
export interface AyahsUpdateResponseData {
    bismillah: string;
    breakers: string;
    number: number;
    sajdah?: any;
    surah: string;
    text: string;
    uuid: string;
}
export interface AyahsPartialupdateRequestData {
    bismillah?: string;
    breakers?: string;
    number?: number;
    sajdah?: any;
    surah?: string;
    text?: string;
    uuid?: string;
}
export interface AyahsPartialupdateResponseData {
    bismillah: string;
    breakers: string;
    number: number;
    sajdah?: any;
    surah: string;
    text: string;
    uuid: string;
}