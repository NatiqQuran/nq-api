
export interface PhrasesModifyRequestData {
    phrases: object;
}
export interface PhrasesModifyResponseData {
    phrases: object;
}
export interface PhrasesModifyRequestParams {
    language: string;
}
export interface PhrasesListResponseData {
}
export interface PhrasesCreateRequestData {
    phrase: string;
    uuid: string;
}
export interface PhrasesCreateResponseData {
    phrase: string;
    uuid: string;
}
export interface PhrasesRetrieveResponseData {
    phrase: string;
    uuid: string;
}
export interface PhrasesUpdateRequestData {
    phrase: string;
    uuid: string;
}
export interface PhrasesUpdateResponseData {
    phrase: string;
    uuid: string;
}
export interface PhrasesPartialupdateRequestData {
    phrase?: string;
    uuid?: string;
}
export interface PhrasesPartialupdateResponseData {
    phrase: string;
    uuid: string;
}