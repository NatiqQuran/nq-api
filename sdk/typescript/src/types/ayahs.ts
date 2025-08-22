import { Word } from "./words";

export type AyahsListResponseData = Ayah[];
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
    sajdah?: string;
    surah: object;
    text: string;
    uuid: string;
    words: Word[];
}
export interface AyahsUpdateRequestData {
    bismillah: string;
    breakers: string;
    number: number;
    sajdah?: string;
    surah: string;
    text: string;
    uuid: string;
}
export interface AyahsUpdateResponseData {
    bismillah: string;
    breakers: string;
    number: number;
    sajdah?: string;
    surah: string;
    text: string;
    uuid: string;
}
export interface AyahsPartialupdateRequestData {
    bismillah?: string;
    breakers?: string;
    number?: number;
    sajdah?: string;
    surah?: string;
    text?: string;
    uuid?: string;
}
export interface AyahsPartialupdateResponseData {
    bismillah: string;
    breakers: string;
    number: number;
    sajdah?: string;
    surah: string;
    text: string;
    uuid: string;
}


export interface Ayah {
    uuid: string;
    number: number;
    text: string;
    bismillah?: string;
    breakers?: string;
    sajdah?: string;
    surah?: string;
}

export interface AyahTranslation {
    uuid: string;
    text: string;
    ayah_uuid: string;
    translation_uuid: string;
    bismillah?: string;
}

export interface AyahInSurah {
    uuid: string;
    number: number;
    sajdah?: string;
    is_bismillah?: boolean;
    bismillah_text?: string;
    text: string;
}