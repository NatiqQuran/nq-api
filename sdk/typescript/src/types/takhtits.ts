
export type TakhtitsAyahs_breakersGetResponseData = AyahBreakersResponse[];
export interface TakhtitsAyahs_breakersPostRequestData {
    ayah_uuid: string;
    type: string;
}
export interface TakhtitsAyahs_breakersPostResponseData {
    type: 'page' | 'juz' | 'hizb' | 'rub' | 'manzil' | 'ruku';
    uuid: string;
}
export interface TakhtitsImportPostResponseData {
}
export interface TakhtitsImportRequestParams {
    type?: string;
}
export type TakhtitsWords_breakersGetResponseData = WordBreakersResponse[];
export interface TakhtitsWords_breakersPostRequestData {
    type: string;
    word_uuid: string;
}
export interface TakhtitsWords_breakersPostResponseData {
    type: string;
    word_uuid: string;
}
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
export interface TakhtitsAyahs_breakersResourceGetResponseData {
    type: 'page' | 'juz' | 'hizb' | 'rub' | 'manzil' | 'ruku';
    uuid: string;
}
export interface TakhtitsWords_breakersResourceGetResponseData {
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