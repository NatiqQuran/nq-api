
export interface TakhtitsListResponseData {
}
export interface TakhtitsListRequestParams {
    mushaf?: string;
}
export interface TakhtitsCreateRequestData {
    account_uuid: string;
    mushaf_uuid: string;
}
export interface TakhtitsCreateResponseData {
    account: number;
    created_at: string;
    creator: number;
    mushaf: number;
    uuid: string;
}
export interface TakhtitsRetrieveResponseData {
    account: number;
    created_at: string;
    creator: number;
    mushaf: number;
    uuid: string;
}
export interface TakhtitsUpdateRequestData {
    account: number;
    created_at: string;
    creator: number;
    mushaf: number;
    uuid: string;
}
export interface TakhtitsUpdateResponseData {
    account: number;
    created_at: string;
    creator: number;
    mushaf: number;
    uuid: string;
}
export interface TakhtitsPartialupdateRequestData {
    account?: number;
    created_at?: string;
    creator?: number;
    mushaf?: number;
    uuid?: string;
}
export interface TakhtitsPartialupdateResponseData {
    account: number;
    created_at: string;
    creator: number;
    mushaf: number;
    uuid: string;
}
export interface TakhtitsTakhtits_ayahs_breakers_listResponseData {
}
export interface TakhtitsTakhtits_ayahs_breakers_createRequestData {
    ayah_uuid: string;
    type: string;
}
export interface TakhtitsTakhtits_ayahs_breakers_createResponseData {
    type: 'page' | 'juz' | 'hizb' | 'rub' | 'manzil' | 'ruku';
    uuid: string;
}
export interface TakhtitsTakhtits_ayahs_breakers_retrieveResponseData {
    type: 'page' | 'juz' | 'hizb' | 'rub' | 'manzil' | 'ruku';
    uuid: string;
}
export interface TakhtitsTakhtits_import_createResponseData {
}
export interface TakhtitsTakhtits_import_createRequestParams {
    type?: string;
}
export interface TakhtitsTakhtits_words_breakers_listResponseData {
}
export interface TakhtitsTakhtits_words_breakers_createRequestData {
    type: string;
    word_uuid: string;
}
export interface TakhtitsTakhtits_words_breakers_createResponseData {
    type: string;
    word_uuid: string;
}
export interface TakhtitsTakhtits_words_breakers_retrieveResponseData {
    type: string;
    word_uuid: string;
}