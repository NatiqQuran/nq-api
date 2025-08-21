
export type TakhtitsListResponseData = Takhtit[];
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
export type TakhtitsTakhtits_ayahs_breakers_listResponseData = AyahBreakersResponse[];
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
export type TakhtitsTakhtits_words_breakers_listResponseData = WordBreakersResponse[];
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


export interface Takhtit {
    uuid: string;
    account: number;
    creator: number;
    mushaf: number;
    created_at: string;
}

export interface AyahBreakersResponse {
    uuid: string;
    type: 'page' | 'juz' | 'hizb' | 'rub' | 'manzil' | 'ruku';
    ayah_uuid: string;
}

export interface WordBreakersResponse {
    uuid: string;
    type: string;
    word_uuid: string;
}