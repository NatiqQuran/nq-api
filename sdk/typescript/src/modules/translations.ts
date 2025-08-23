import * as TranslationsType from "../types/translations";
import { AxiosResponse } from "axios";
import { Connection } from "../client/connection";
import { BaseController } from "../utils/baseController";
import { RequestConfig } from "../utils/globalTypes";

export class TranslationsAyahs extends BaseController {
    constructor(conn: Connection, token?: string) {
        super(conn, token);
    }
    /** GET /translations/{uuid}/ayahs/ */
    async translations_ayahs_list(uuid: string, config?: RequestConfig<TranslationsType.TranslationsAyahsRequestParams>
    ): Promise<AxiosResponse<TranslationsType.TranslationsAyahsGetResponseData>> {
        return await this.axiosGet(`/translations/${uuid}/ayahs/`, config);
    }
}

export class TranslationsImport extends BaseController {
    constructor(conn: Connection, token?: string) {
        super(conn, token);
    }
    /** POST /translations/import/ */
    async translations_import_create(config?: RequestConfig
    ): Promise<AxiosResponse<TranslationsType.TranslationsImportPostResponseData>> {
        return await this.axiosPost(`/translations/import/`, config);
    }
}
export class TranslationsAyahsResource extends BaseController {
    constructor(conn: Connection, token?: string) {
        super(conn, token);
    }
    /** GET /translations/{uuid}/ayahs/{ayah_uuid}/ */
    async translations_ayahs_retrieve(uuid: string, ayah_uuid: string, config?: RequestConfig
    ): Promise<AxiosResponse<TranslationsType.TranslationsAyahsResourceGetResponseData>> {
        return await this.axiosGet(`/translations/${uuid}/ayahs/${ayah_uuid}/`, config);
    }
    /** POST /translations/{uuid}/ayahs/{ayah_uuid}/ */
    async translations_ayahs_create(uuid: string, ayah_uuid: string, data: TranslationsType.TranslationsAyahsResourcePostRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<TranslationsType.TranslationsAyahsResourcePostResponseData>> {
        return await this.axiosPost(`/translations/${uuid}/ayahs/${ayah_uuid}/`, data, config);
    }
    /** PUT /translations/{uuid}/ayahs/{ayah_uuid}/ */
    async translations_ayahs_update(uuid: string, ayah_uuid: string, data: TranslationsType.TranslationsAyahsResourcePutRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<TranslationsType.TranslationsAyahsResourcePutResponseData>> {
        return await this.axiosPut(`/translations/${uuid}/ayahs/${ayah_uuid}/`, data, config);
    }
}

export class TranslationsController extends BaseController {
    public readonly ayahs: TranslationsAyahs;
    public readonly import: TranslationsImport;
    public readonly ayahs_resource: TranslationsAyahsResource;

    constructor(connection: Connection, token?: string) {
        super(connection, token);
        this.ayahs = new TranslationsAyahs(this.conn);
        this.import = new TranslationsImport(this.conn);
        this.ayahs_resource = new TranslationsAyahsResource(this.conn);
    }
    
    /** GET /translations/ */
    async list(config?: RequestConfig<TranslationsType.TranslationsListRequestParams>
    ): Promise<AxiosResponse<TranslationsType.TranslationsListResponseData>> {
        return await this.axiosGet(`/translations/`, config);
    }
    
    /** POST /translations/ */
    async create(data: TranslationsType.TranslationsCreateRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<TranslationsType.TranslationsCreateResponseData>> {
        return await this.axiosPost(`/translations/`, data, config);
    }
    
    /** GET /translations/{uuid}/ */
    async retrieve(uuid: string, config?: RequestConfig
    ): Promise<AxiosResponse<TranslationsType.TranslationsRetrieveResponseData>> {
        return await this.axiosGet(`/translations/${uuid}/`, config);
    }
    
    /** PUT /translations/{uuid}/ */
    async update(uuid: string, data: TranslationsType.TranslationsUpdateRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<TranslationsType.TranslationsUpdateResponseData>> {
        return await this.axiosPut(`/translations/${uuid}/`, data, config);
    }
    
    /** PATCH /translations/{uuid}/ */
    async partialUpdate(uuid: string, data: TranslationsType.TranslationsPartialupdateRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<TranslationsType.TranslationsPartialupdateResponseData>> {
        return await this.axiosPatch(`/translations/${uuid}/`, data, config);
    }
    
    /** DELETE /translations/{uuid}/ */
    async delete(uuid: string, config?: RequestConfig
    ): Promise<AxiosResponse<any>> {
        return await this.axiosDelete(`/translations/${uuid}/`, config);
    }
    
}