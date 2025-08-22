import { AyahTranslation } from "./ayahs";

export type TranslationsAyahsGetResponseData = AyahTranslation[];
export interface TranslationsAyahsRequestParams {
    limit?: number;
    offset?: number;
    ordering?: string;
    search?: string;
    surah_uuid?: string;
}
export interface TranslationsImportPostResponseData {
    language: string;
    mushaf_uuid: string;
    release_date?: string;
    source?: string;
    status?: 'draft' | 'pending_review' | 'published';
    translator_uuid: string;
    uuid: string;
}
export type TranslationsListResponseData = TranslationList[];
export interface TranslationsListRequestParams {
    language?: string;
    limit?: number;
    mushaf: string;
    offset?: number;
    ordering?: string;
    search?: string;
}
export interface TranslationsCreateRequestData {
    language: string;
    mushaf_uuid: string;
    release_date?: string;
    source?: string;
    status?: 'draft' | 'pending_review' | 'published';
    translator_uuid: string;
    uuid: string;
}
export interface TranslationsCreateResponseData {
    language: string;
    mushaf_uuid: string;
    release_date?: string;
    source?: string;
    status?: 'draft' | 'pending_review' | 'published';
    translator_uuid: string;
    uuid: string;
}
export interface TranslationsRetrieveResponseData {
    language: 'ar' | 'en' | 'fr' | 'ur' | 'tr' | 'id' | 'fa' | 'ru' | 'es' | 'de' | 'bn' | 'zh' | 'ms' | 'hi' | 'sw' | 'ps' | 'ku' | 'az' | 'ha' | 'so' | 'ta' | 'te' | 'ml' | 'pa' | 'sd' | 'ug' | 'uz' | 'kk' | 'ky' | 'tk' | 'tg' | 'syr' | 'ber' | 'am' | 'om' | 'wo' | 'yo' | 'other';
    mushaf_uuid: string;
    release_date?: string;
    source?: string;
    status?: 'draft' | 'pending_review' | 'published';
    translator_uuid: string;
    uuid: string;
}
export interface TranslationsUpdateRequestData {
    language: string;
    mushaf_uuid: string;
    release_date?: string;
    source?: string;
    status?: 'draft' | 'pending_review' | 'published';
    translator_uuid: string;
    uuid: string;
}
export interface TranslationsUpdateResponseData {
    language: string;
    mushaf_uuid: string;
    release_date?: string;
    source?: string;
    status?: 'draft' | 'pending_review' | 'published';
    translator_uuid: string;
    uuid: string;
}
export interface TranslationsPartialupdateRequestData {
    language?: string;
    mushaf_uuid?: string;
    release_date?: string;
    source?: string;
    status?: 'draft' | 'pending_review' | 'published';
    translator_uuid?: string;
    uuid?: string;
}
export interface TranslationsPartialupdateResponseData {
    language: string;
    mushaf_uuid: string;
    release_date?: string;
    source?: string;
    status?: 'draft' | 'pending_review' | 'published';
    translator_uuid: string;
    uuid: string;
}
export interface TranslationsAyahsResourceGetResponseData {
    ayah_uuid: string;
    bismillah?: string;
    text: string;
    translation_uuid: string;
    uuid: string;
}
export interface TranslationsAyahsResourcePostRequestData {
    bismillah?: boolean;
    text: string;
}
export interface TranslationsAyahsResourcePostResponseData {
    ayah_uuid: string;
    bismillah?: string;
    text: string;
    translation_uuid: string;
    uuid: string;
}
export interface TranslationsAyahsResourcePutRequestData {
    bismillah?: boolean;
    text: string;
}
export interface TranslationsAyahsResourcePutResponseData {
    ayah_uuid: string;
    bismillah?: string;
    text: string;
    translation_uuid: string;
    uuid: string;
}


export interface TranslationList {
    uuid: string;
    language: string;
    source?: string;
    release_date?: string;
    status?: 'draft' | 'pending_review' | 'published';
    translator_uuid: string;
    mushaf_uuid: string;
}